import discord
from discord import app_commands
from discord import Color as c
from discord.ext import commands
import SqliteClasses
from Classes import character, player
import json
from helper import *
from os import path
import Paginator

file = path.join(path.dirname(__file__), 'cogs/jsons')

Character = character.Character
Player = player.Player


class Market(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    market = app_commands.Group(name="market", description="This a market group!")

    @market.command(description="Main Market Display")
    async def display(self, interaction, *, filters: str = '-page 1'):
        p = Paginator
        embeds = []

        characterlist = SqliteClasses.fetchallQuery("SELECT * from Characters WHERE market > 0", [])
        charlist = []
        for i in characterlist:
            charlist.append(list(i))
        characterlist = charlist
        for i in range(len(characterlist)):
            characterlist[i].insert(0, str(i + 1))
        stri = filters.split('-')
        stri.pop(0)
        newList = []
        for value in stri:
            newList.append(value.split())

        page = 1
        for filter in newList:
            if filter[0].lower() == 'page':
                page = int(filter[1])
            elif filter[0].lower() == 'minatk':
                characterlist = [i for i in characterlist if i[5] >= int(filter[1])]
            elif filter[0].lower() == 'maxatk':
                characterlist = [i for i in characterlist if i[5] <= int(filter[1])]
            elif filter[0].lower() == 'minhp':
                characterlist = [i for i in characterlist if i[15] >= int(filter[1])]
            elif filter[0].lower() == 'maxhp':
                characterlist = [i for i in characterlist if i[15] <= int(filter[1])]
            elif filter[0].lower() == 'mindef':
                characterlist = [i for i in characterlist if i[6] >= int(filter[1])]
            elif filter[0].lower() == 'maxdef':
                characterlist = [i for i in characterlist if i[6] <= int(filter[1])]
            elif filter[0].lower() == 'minspd':
                characterlist = [i for i in characterlist if i[7] >= int(filter[1])]
            elif filter[0].lower() == 'maxspd':
                characterlist = [i for i in characterlist if i[7] <= int(filter[1])]
            elif filter[0].lower() == 'mincrit':
                characterlist = [i for i in characterlist if i[8] >= int(filter[1])]
            elif filter[0].lower() == 'maxcrit':
                characterlist = [i for i in characterlist if i[8] <= int(filter[1])]
            elif filter[0].lower() == 'minmagdef':
                characterlist = [i for i in characterlist if i[9] >= int(filter[1])]
            elif filter[0].lower() == 'maxmagdef':
                characterlist = [i for i in characterlist if i[9] <= int(filter[1])]
            elif filter[0].lower() == 'minmagatk':
                characterlist = [i for i in characterlist if i[10] >= int(filter[1])]
            elif filter[0].lower() == 'maxmagatk':
                characterlist = [i for i in characterlist if i[10] <= int(filter[1])]
            elif filter[0].lower() == 'minlvl':
                characterlist = [i for i in characterlist if i[13] >= int(filter[1])]
            elif filter[0].lower() == 'maxlvl':
                characterlist = [i for i in characterlist if i[13] <= int(filter[1])]
            elif filter[0].lower() == 'collectionid':
                characterlist = [i for i in characterlist if i[11] == int(filter[1])]
            elif filter[0].lower() == 'locked':
                characterlist = [i for i in characterlist if i[14] == 1]
            elif filter[0].lower() == 'unlocked':
                characterlist = [i for i in characterlist if i[14] == 0]
            elif filter[0].lower() == 'rarity':
                characterlist = [i for i in characterlist if i[18] == int(filter[1])]
            elif filter[0].lower() == 'name':
                characterlist = [i for i in characterlist if " ".join(filter[1:]).lower() in i[3].lower()]
        if 0 >= page or page > math.floor((len(characterlist) - 1) / 25) + 1:
            await interaction.response.send_message("Page doesnt exist!")
            return
        for page in range(math.floor((len(characterlist) - 1) / 25) + 1):
            embed = discord.Embed(title="Global Market :shopping_cart:",
                                  description="All the characters that have been put up for sale are listed below!",
                                  color=c.teal())
            embed.set_footer(text=f'Page {page + 1} /{math.floor((len(characterlist) - 1) / 25) + 1}')
            min = (25 * page)
            max = (25 * page) + 25
            for character in characterlist[min:max]:
                gold = "{:,}".format(character[19])
                embed.add_field(name=f"{character[3]} | Gold: __{gold}__",
                                value=f"{rarityName.get(str(character[18]))} | Level {character[13]} | {character[26]} | Global ID: {character[1]}")
                embed.set_image(url=data[character[11] - 1]["url"])
                embed.set_thumbnail(url=data[(characterlist[min][11] - 1)]["url"])

            embeds.append(embed)

        await p.Simple().start(interaction, pages=embeds)

    @market.command(description="Put your character up for sale on the market")
    async def sell(self, interaction, character: int, price: int):
        charlist = SqliteClasses.charactercollection(interaction.user.id)
        p = Player(interaction.user.id)
        listings = SqliteClasses.fetchallQuery("SELECT * from Characters WHERE owner_id = ? AND market > 0",
                                               [interaction.user.id])

        if character is None or price is None or character < 1 or price < 1 or character > len(charlist):
            await interaction.response.send_message(
                f"Missing arguments found!\n Proper input: /market sell <character number> <price>")
        elif len(listings) == 10:
            await interaction.response.send_message("You can only have 10 active listings at a time on the market!")
        elif charlist[character - 1][13] != 0:
            await interaction.response.send_message("This character is locked!")
        elif charlist[character - 1][19] != 0:
            await interaction.response.send_message("This character is in a raid!")
        elif charlist[character - 1][16] != 0:
            await interaction.response.send_message("This character has a skin!")
        elif 10000 > price > 10000000:
            await interaction.response.send_message("You can't sell for this price!")
        else:
            num = character - 1
            if p.selectedchar is not None and int(p.selectedchar) == int(charlist[num][0]):
                SqliteClasses.updateQuery("UPDATE Users SET selectedcharacter = NULL WHERE user_id = ?",
                                          [interaction.user.id])

            SqliteClasses.updateQuery("UPDATE Characters SET market = ? WHERE global_id = ?", [price, charlist[num][0]])
            await interaction.response.send_message(f"Your {charlist[num][2]} was put on the market!")

    @market.command(description="Buy a character off the market")
    async def buy(self, interaction, character: int):
        stock = SqliteClasses.fetchoneQuery("SELECT * from Characters WHERE global_id = ? AND market > 0", [character])

        if character is None or character < 1:
            await interaction.response.send_message(
                f"Missing argument found!\n Proper input: /market buy <market number>")
        elif stock is None:
            await interaction.response.send_message("Specified character was not found.")
        else:

            p = Player(interaction.user.id)

            gold = '{:,}'.format(stock[18] - p.gold)
            if p.gold < stock[18]:
                await interaction.response.send_message(f"You need __{gold}__ more gold to buy this listing.")
            else:

                SqliteClasses.updateQuery("UPDATE Users SET gold = gold - ? WHERE user_id = ?",
                                          [stock[18], interaction.user.id])
                SqliteClasses.updateQuery("UPDATE Users SET gold = gold + ? WHERE user_id = ?", [stock[18], stock[1]])
                SqliteClasses.updateQuery("UPDATE Characters SET owner_id = ?, market = 0 WHERE global_id = ?",
                                          [interaction.user.id, character])
                await interaction.response.send_message(f"You purchased {stock[2]}!")

    @market.command(description="Check what characters you have for sale on the market")
    async def listings(self, interaction):
        listings = SqliteClasses.fetchallQuery("SELECT * from Characters WHERE owner_id = ? AND market > 0",
                                               [interaction.user.id])
        if len(listings) >= 1:
            embed = discord.Embed(title="Listings :newspaper:",
                                  description="These are your current listings on the global market:\n", color=c.teal())
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
            i = 0
            for character in listings:
                i = i + 1
                embed.add_field(name=f"{i}) {character[2]}",
                                value=f"`{'{:,}'.format(character[18])}` <:gold:844956181055537182>", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You have no active listings.")

    @market.command(description="Remove a character you have for sale on the market")
    async def remove(self, interaction, number: int):
        if number is None:
            await interaction.response.send_message(
                f'Character not found! Use `/collection` to view your characters and their number!'
                f'\nProper Formatting: `/info [character number]`')
        else:
            num = number - 1
            inv = SqliteClasses.fetchallQuery("SELECT * from Characters WHERE owner_id = ? AND market > 0",
                                              [interaction.user.id])
            p = Player(interaction.user.id)
            chardata = Character(p.selectedchar)
            if number < 1 or number > len(inv):
                await interaction.response.send_message(
                    f"Character not found!\nProper Formatting: `/market remove [character number]`")
            elif chardata is not None and chardata.raiding == 1:
                await interaction.response.send_message("You can't switch characters while in a raid!")
            else:
                global_id = inv[num][0]
                SqliteClasses.updateQuery("UPDATE Characters SET market = 0 WHERE global_id = ?", [global_id])
                await interaction.response.send_message(f"Your {inv[num][2]} was taken off the market.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Market(bot))
    print("Market is Loaded")