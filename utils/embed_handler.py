from typing import Union
import constants
from discord import Embed, Color, Member, User

def get_top_role_color(member: Union[Member, User], *, fallback_color) -> Color:
    """
    Tries to get member top role color and if fails returns fallback_color - This makes it work in DMs.
    Also if the top role has default role color then returns fallback_color.
    :param member: Member to get top role color from. If it's a User then default discord color will be returned.
    :param fallback_color: Color to use if the top role of param member is default color or if param member is
                           discord.User (DMs)
    :return: discord.Color
    """
    try:
        color = member.top_role.color
    except AttributeError:
        # Fix for DMs
        return fallback_color

    if color == Color.default():
        return fallback_color
    else:
        return color



def simple_embed(message: str, title: str, color: Color) -> Embed:
    embed = Embed(title=title, description=message, color=color)
    return embed


def info(message: str, member: Union[Member, User], title: str = "Info") -> Embed:
    """
    Constructs success embed with custom title and description.
    Color depends on passed member top role color.
    :param message: embed description
    :param member: member object to get the color of it's top role from
    :param title: title of embed, defaults to "Info"
    :return: Embed object
    """
    return Embed(title=title, description=message, color=get_top_role_color(member, fallback_color=Color.green()))


def success(message: str, member: Union[Member, User] = None) -> Embed:
    """
    Constructs success embed with fixed title 'Success' and color depending
    on passed member top role color.
    If member is not passed or if it's a User (DMs) green color will be used.
    :param message: embed description
    :param member: member object to get the color of it's top role from,
                   usually our bot member object from the specific guild.
    :return: Embed object
    """
    return simple_embed(f"{constants.success_emoji}︱{message}", "",
                        get_top_role_color(member, fallback_color=Color.green()))


def warning(message: str) -> Embed:
    """
    Constructs warning embed with fixed title 'Warning' and color gold.
    :param message: embed description
    :return: Embed object
    """
    return simple_embed(f":warning:︱{message}", "", Color.dark_gold())


def failure(message: str) -> Embed:
    """
    Constructs failure embed with fixed title 'Failure' and color red
    :param message: embed description
    :return: Embed object
    """
    return simple_embed(f"{constants.failure_emoji}︱{message}", "", Color.red())

def authored(message: str, *, author: Union[Member, User]) -> Embed:
    """
    Construct embed and sets its author to passed param author.
    Embed color is based on passed author top role color.
    :param author: to whom the embed will be authored.
    :param message: message to display in embed.
    :return: discord.Embed
    """
    embed = Embed(description=message, color=get_top_role_color(author, fallback_color=Color.green()))
    embed.set_author(name=author.name, icon_url=author.display_avatar.url)
    return embed

def black_jack_template(author: User, player, description: str, color: Color) -> Embed:
    """
    Creates black jack embed template.
    :param author: User discord user from which to get name and avatar
    :param player: player object
    :param description: embed description
    :param color: discord.Color
    :return: discord.Embed
    """
    embed = authored(description, author=author)
    embed.colour = color
    embed.set_thumbnail(
        url="https://www.vhv.rs/dpng/d/541-5416003_poker-club-icon-splash-diwali-coasters-black-background.png"
    )
    card_string = player.get_emote_string(hidden=False)
    embed.add_field(name="Your hand", value=f"{card_string}")
    embed.set_footer(
        text="BlackJack",
        icon_url="https://i.pinimg.com/originals/c3/5f/63/c35f630a4efb237206ec94f8950dcad5.png"
    )
    return embed


def black_jack_embed(user: User, player, outcome: str = None, hidden: bool = True) -> Embed:
    """
    Creates embed based on set of constraints for blackjack
    :param user:  discord.User
    :param player: player object for blackjack
    :param outcome: blackjack game outcome
    :param hidden: dealer card value
    :return: discord.Embed
    """
    embed = black_jack_template(user, player, "", Color.gold())
    embed.add_field(name="Dealer hand", value=player.game.dealer.get_emote_string(hidden=hidden))
    if outcome == "win":
        embed.colour = Color.dark_green()
        embed.description = "**Outcome:** You won!"
    elif outcome == "lose":
        embed.colour = Color.dark_red()
        embed.description = "**Outcome:** You lost!"
    elif outcome == "tie":
        embed.colour = Color.dark_grey()
        embed.description = "**Outcome:** It's a tie!"
    return embed


