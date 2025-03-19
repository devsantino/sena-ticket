import discord
from discord.ext import commands
from discord import ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from discord import app_commands
import os  # استيراد مكتبة os للوصول إلى متغيرات البيئة
from dotenv import load_dotenv

# إعدادات الفئات
CATEGORY_OPEN = "📂 التيكتات المفتوحة"
CATEGORY_CLOSED = "📁 التيكتات المغلقة"

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 إنشاء تيكت", style=ButtonStyle.green)
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        select_view = TicketSelectView()
        await interaction.response.send_message("📋 اختر نوع التيكت من القائمة: ", view=select_view, ephemeral=True)

class TicketSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="اختر نوع الطلب...",
        options=[
            SelectOption(label="طلب خدمة", description="للطلبات الجديدة"),
            SelectOption(label="تجديد خدمة", description="لتجديد خدماتك"),
            SelectOption(label="استفسار", description="لطرح سؤال")
        ]
    )
    async def select_option(self, interaction: discord.Interaction, select: Select):
        category = discord.utils.get(interaction.guild.categories, name=CATEGORY_OPEN)
        if not category:
            category = await interaction.guild.create_category(CATEGORY_OPEN)

        channel = await category.create_text_channel(f"🎫-{interaction.user.name}")
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        embed = discord.Embed(title="📩 تيكت جديد", description=f"نوع الطلب: **{select.values[0]}**", color=discord.Color.green())
        close_view = CloseTicketView()
        await channel.send(embed=embed, view=close_view)
        await interaction.response.send_message(f"✅ تم إنشاء تيكتك بنجاح: {channel.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ إغلاق التيكت", style=ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        confirm_view = ConfirmCloseView()
        await interaction.response.send_message("⚠️ هل أنت متأكد أنك تريد إغلاق هذه التيكت؟", view=confirm_view, ephemeral=True)

class ConfirmCloseView(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="تأكيد", style=ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        closed_category = discord.utils.get(interaction.guild.categories, name=CATEGORY_CLOSED)
        if not closed_category:
            closed_category = await interaction.guild.create_category(CATEGORY_CLOSED)

        await interaction.channel.edit(category=closed_category)
        await interaction.response.send_message("✅ تم إغلاق التيكت بنجاح!", ephemeral=True)

    @discord.ui.button(label="إلغاء", style=ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("❌ تم إلغاء عملية الإغلاق!", ephemeral=True)

class TicketBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def on_ready(self):
        print(f'✅ تم تسجيل الدخول كبوت: {self.user}')
        try:
            synced = await bot.tree.sync()
            print(f"✅ {len(synced)} أمر سلاش تم تسجيله بنجاح!")
        except Exception as e:
            print(f"❌ حدث خطأ أثناء تسجيل الأوامر: {e}")

# إنشاء البوت
bot = TicketBot()

# أمر سلاش لإعداد نظام التيكت
@bot.tree.command(name="setup", description="إعداد نظام التيكت")
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(title="🛠️ نظام التيكت", description="اضغط على الزر أدناه لإنشاء تيكت جديد.", color=discord.Color.blue())
    view = TicketView()
    await interaction.response.send_message(embed=embed, view=view)

# تشغيل البوت
load_dotenv()  # تحميل المتغيرات من ملف .env
TOKEN = os.getenv("TOKEN")
