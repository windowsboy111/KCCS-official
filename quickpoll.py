import discord
import base64
from discord.ext import commands


class QuickPoll:
    """"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def quickpoll(self, ctx, msg, question, options: str):
        if len(options) <= 1:
            await msg.edit(content='You need more than one option to make a poll!')
            return
        if len(options) > 26:
            await msg.edit(content='You cannot make a poll for more than 10 things!')
            return

        if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
            reactions = ['✅', '❌']
        elif len(options) <= 10:
            reactions = ['1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣','🔟']
        else:
            reactions = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿','0️⃣','1️⃣','2️⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣','🔟']

        description = []
        for x, option in enumerate(options):
            description += '\n {} {}'.format(reactions[x], option)
        embed = discord.Embed(title=question, description=''.join(description),color=0x00FFBB)
        embed.set_author(name=ctx.message.author,icon_url=ctx.message.author.avatar_url)
        react_message = await msg.edit(embed=embed)
        react_msg = react_message
        i=0
        for reaction in reactions[:len(options)]:
            if i == 20:
                msg = await ctx.send('And more reactions...')
            await msg.add_reaction(reaction)
            i+=1
        id = str(msg.id)
        id = base64.b64encode(id.encode("utf-8"))
	    id = str(id, "utf-8")
        text = 'Poll ID: {}'.format(msg.id, id)
        if i > 10:
            text = "Can't tally this poll :("
        embed.set_footer(text=text)
        await msg.edit(embed=embed)

    @commands.command(pass_context=True)
    async def tally(self, ctx, msg, id):
        try: poll_message = await discord.TextChannel.fetch_message(ctx.message.channel, id)
        except: return 1
        if not poll_message.embeds:
            await msg.edit(content='No embeds have been found')
            return 2
        embed = poll_message.embeds[0]
        if poll_message.author != ctx.message.guild.me: return 2
        try: t = embed.description.split('\n')
        except: return 1
        unformatted_options = [x.strip() for x in embed.description.split('\n')]
        opt_dict = {x[:2]: x[3:] for x in unformatted_options} if unformatted_options[0][0] == '1' \
            else {x[:1]: x[2:] for x in unformatted_options}
        # check if we're using numbers for the poll, or x/checkmark, parse accordingly
        voters = [ctx.message.guild.me.id]  # add the bot's ID to the list of voters to exclude it's votes

        tally = {x: 0 for x in opt_dict.keys()}
        for reaction in poll_message.reactions:
            if reaction.emoji in opt_dict.keys():
                reactions = poll_message.reactions
                for reaction in reactions:
                    async for reactor in reaction.users():
                        if reactor.id not in voters:
                            try:
                                tally[reaction.emoji] += 1
                            except KeyError:
                                continue
                            voters.append(reactor.id)

        output = discord.Embed(title='Results of the poll for "{}":\n'.format(embed.title),color=0xb6ff00)
        for key in tally.keys():
            output.add_field(name=opt_dict[key],value=tally[key])
            output.set_footer(text='Poll ID: {}'.format(id))
        await msg.edit(embed=output)
        edited = discord.Embed(title=embed.title,description='Poll ended',color=0xFFC300)
        edited.set_footer(text=f"Result id: {msg.id}")
        await poll_message.edit(embed=edited)


def setup(bot):
    bot.add_cog(QuickPoll(bot))
