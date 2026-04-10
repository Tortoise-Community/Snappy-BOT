import discord
from discord import app_commands
from discord.ext import commands

from utils.gambling_backend import Game, Player
from utils.embed_handler import black_jack_embed


class BlackjackView(discord.ui.View):
    def __init__(self, cog, player: Player):
        super().__init__(timeout=60)
        self.cog = cog
        self.player = player

    async def process_turn(self, interaction: discord.Interaction):
        # Update internal value
        val = self.player.calculate_card_value()

        # If busted or 21, they are forced to stay
        if val >= 21:
            self.player.stay = True
            self.stop()  # Disables buttons
            await self.cog.check_active_session(self.player, interaction)
        else:
            # Game continues, just update the embed
            embed = black_jack_embed(interaction.user, self.player)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player.user_id:
            return await interaction.response.send_message("Not your game!", ephemeral=True)

        self.player.cards.append(self.player.game.deck.draw())
        await self.process_turn(interaction)

    @discord.ui.button(label="Stay", style=discord.ButtonStyle.blurple)
    async def stay(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player.user_id:
            return await interaction.response.send_message("Not your game!", ephemeral=True)

        self.player.stay = True
        self.stop()
        await self.cog.check_active_session(self.player, interaction)

    @discord.ui.button(label="Double", style=discord.ButtonStyle.gray)
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player.user_id:
            return await interaction.response.send_message("Not your game!", ephemeral=True)

        self.player.bet_amount *= 2
        self.player.cards.append(self.player.game.deck.draw())
        self.player.stay = True
        self.stop()
        await self.cog.check_active_session(self.player, interaction)


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live_games = {}

    async def check_active_session(self, player: Player, interaction: discord.Interaction):
        game = player.game
        all_finished = all(p.stay or p.calculate_card_value() >= 21 for p in game.participants.values())

        if all_finished:
            # Play dealer hand
            while game.dealer.calculate_card_value() < 17:
                game.dealer.cards.append(game.deck.draw())

            # Final Results
            dealer_val = game.dealer.calculate_card_value()
            player_val = player.calculate_card_value()

            outcome = "tie"
            if player_val > 21:
                outcome = "lose"
            elif dealer_val > 21:
                outcome = "win"
            elif player_val > dealer_val:
                outcome = "win"
            elif player_val < dealer_val:
                outcome = "lose"

            final_embed = black_jack_embed(interaction.user, player, outcome=outcome, hidden=False)
            await interaction.response.edit_message(embed=final_embed, view=None)

            # Cleanup
            if game.channel_id in self.live_games:
                del self.live_games[game.channel_id]
        else:
            # Other players are still playing in this channel
            embed = black_jack_embed(interaction.user, player)
            embed.description = "Waiting for other players..."
            await interaction.response.edit_message(embed=embed, view=None)

    @app_commands.command(name="blackjack", description="Play blackjack")
    async def blackjack(self, interaction: discord.Interaction, bet: int = 10):
        if interaction.channel_id not in self.live_games:
            self.live_games[interaction.channel_id] = Game(interaction.channel_id)
            # Deal dealer's starting hand
            self.live_games[interaction.channel_id].dealer.cards.append(
                self.live_games[interaction.channel_id].deck.draw())
            self.live_games[interaction.channel_id].dealer.cards.append(
                self.live_games[interaction.channel_id].deck.draw())

        game = self.live_games[interaction.channel_id]

        if interaction.user.id in game.participants:
            return await interaction.response.send_message("Already in game!", ephemeral=True)

        player = Player(interaction.user.id, bet, game)
        game.participants[interaction.user.id] = player
        player.cards.append(game.deck.draw())
        player.cards.append(game.deck.draw())

        if player.calculate_card_value() == 21:
            player.stay = True

        view = BlackjackView(self, player)
        embed = black_jack_embed(interaction.user, player)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Games(bot))