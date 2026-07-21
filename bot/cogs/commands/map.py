# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀▀░█▀█░█▀▄░█▀▀░█░█   ░█▀▄░█▀▀░█░█░█▀▀                     ║
# ║   ░█░░░█░█░█░█░█▀▀░▄▀▄   ░█░█░█▀▀░▀▄▀░▀▀█                     ║
# ║   ░▀▀▀░▀▀▀░▀▀░░▀▀▀░▀░▀   ░▀▀░░▀▀▀░░▀░░▀▀▀                     ║
# ║                                                                  ║
# ║            © 2026 CodeX Devs — All Rights Reserved              ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/codexdev                      ║
# ║   youtube  ──  https://youtube.com/@CodeXDevs                   ║
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
from utils.emoji import DELETE
from discord.ext import commands
from discord import ui, ButtonStyle, SelectOption
from discord.ui import LayoutView, TextDisplay, Separator, ActionRow, MediaGallery
import requests
import asyncio
from utils.Tools import *
from utils.cv2 import CV2, build_container
from utils.config import *
class MapView(LayoutView):
    def __init__(self, bot, location, ctx):
        super().__init__(timeout=None)
        self.bot = bot
        self.location = location
        self.ctx = ctx
        self.zoom_level = 14
        self.map_style = 'map'
        self.map_size = '1200,900'
        self.coordinates = self.get_coordinates(location)
        self.latitude, self.longitude = None, None
        if self.coordinates != (None, None):
            self.latitude, self.longitude = float(self.coordinates[0]), float(self.coordinates[1])
        
        self.update_map()

        b_left = ui.Button(label="", emoji="⬅️", style=ButtonStyle.secondary)
        b_left.callback = self.move_left
        b_up = ui.Button(label="", emoji="⬆️", style=ButtonStyle.secondary)
        b_up.callback = self.move_up
        b_delete = ui.Button(label="", emoji=DELETE, style=ButtonStyle.danger)
        b_delete.callback = self.delete_embed
        b_down = ui.Button(label="", emoji="⬇️", style=ButtonStyle.secondary)
        b_down.callback = self.move_down
        b_right = ui.Button(label="", emoji="➡️", style=ButtonStyle.secondary)
        b_right.callback = self.move_right

        self.add_item(ActionRow(b_left, b_up, b_delete, b_down, b_right))

        b_zin = ui.Button(label="Zoom In", style=ButtonStyle.primary)
        b_zin.callback = self.zoom_in
        b_zout = ui.Button(label="Zoom Out", style=ButtonStyle.primary)
        b_zout.callback = self.zoom_out
        b_coords = ui.Button(label="Enter Coordinates", style=ButtonStyle.primary)
        b_coords.callback = self.enter_coordinates
        b_addr = ui.Button(label="Enter Address", style=ButtonStyle.success)
        b_addr.callback = self.enter_address

        self.add_item(ActionRow(b_zin, b_zout, b_coords, b_addr))

        self.add_item(ActionRow(MapStyleSelect(self)))
        self.add_item(ActionRow(MapSizeSelect(self)))

        self.build_ui()

    def build_ui(self):
        
        container = build_container(
            TextDisplay(f"**Map of {self.location}**"),
            Separator(visible=True),
            TextDisplay(
                f"🌐 **[Open in Webpage](https://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}&zoom={self.zoom_level})**\n"
                f"🔍 **Current Zoom Level:** {str(self.zoom_level)}\n"
                f"🗺️ **Map Style:** {self.map_style}\n"
                f"📏 **Map Size:** {self.map_size}\n"
                f"📍 **Current Coordinates:** {self.latitude}, {self.longitude}"
            )
        )
        
        gallery = MediaGallery()
        gallery.add_item(media=self.map_url)
        container.add_item(gallery)
        
        
        self.children = [c for c in self.children if not isinstance(c, type(container))]
        self.add_item(container)


    def get_coordinates(self, location):
        try:
            headers = {'User-Agent': f'{BRAND_NAME} Bot (https://codexdevs.in)'}
            response = requests.get(f'https://nominatim.openstreetmap.org/search?q={location}&format=json', headers=headers)
            response.raise_for_status()
            data = response.json()[0]
            return data['lat'], data['lon']
        except (requests.RequestException, IndexError) as e:
            print(f"Failed to get coordinates: {e}")
            return None, None

    def update_map(self):
        if self.latitude is None or self.longitude is None:
            return
        self.map_url = f'https://www.mapquestapi.com/staticmap/v5/map?key=E2SaL3qiTpXQ43nxZFBp0wzEnBI6pqbG&center={self.latitude},{self.longitude}&zoom={self.zoom_level}&size={self.map_size}&type={self.map_style}'
        self.build_ui()

    async def update_embed(self, interaction: discord.Interaction):
        if self.latitude is None or self.longitude is None:
            await interaction.response.send_message("Failed to retrieve map data. Please try again.", ephemeral=True)
            return
        
        try:
            await interaction.message.edit(view=self)
        except Exception as e:
            await interaction.response.send_message(f"Error updating message: {e}", ephemeral=True)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.ctx.author:
            await interaction.response.send_message(
                view=CV2("⚠️ Access Denied", "Sorry only the requested author can control this"),
                ephemeral=True
            )
            return False
        return True

    async def move_left(self, interaction: discord.Interaction):
        if self.longitude is not None:
            self.longitude -= 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Map Updated", "Moved left."), ephemeral=True)
    
    async def move_up(self, interaction: discord.Interaction):
        if self.latitude is not None:
            self.latitude += 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Map Updated", "Moved up."), ephemeral=True)

    async def delete_embed(self, interaction: discord.Interaction):
        try:
            await interaction.message.delete()
        except Exception as e:
            await interaction.response.send_message(f"Error deleting message: {e}", ephemeral=True)

    async def move_down(self, interaction: discord.Interaction):
        if self.latitude is not None:
            self.latitude -= 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Map Updated", "Moved down."), ephemeral=True)

    async def move_right(self, interaction: discord.Interaction):
        if self.longitude is not None:
            self.longitude += 0.01
            self.update_map()
            await self.update_embed(interaction)
            await interaction.response.send_message(view=CV2("✅ Map Updated", "Moved right."), ephemeral=True)
    
    async def zoom_in(self, interaction: discord.Interaction):
        print("Zooming in")
        self.zoom_level = min(self.zoom_level + 1, 18)
        self.update_map()
        await self.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Map Updated", "Zoomed in."), ephemeral=True)

    async def zoom_out(self, interaction: discord.Interaction):
        print("Zooming out")
        self.zoom_level = max(self.zoom_level - 1, 0)
        self.update_map()
        await self.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Map Updated", "Zoomed Out."), ephemeral=True)

    async def enter_coordinates(self, interaction: discord.Interaction):
        await interaction.response.send_message("Please enter the coordinates (latitude, longitude):", ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            coords_msg = await self.bot.wait_for('message', check=check, timeout=60)
            coords = coords_msg.content.split(',')
            if len(coords) == 2:
                self.latitude, self.longitude = float(coords[0].strip()), float(coords[1].strip())
                self.update_map()
                await self.update_embed(interaction)
                await interaction.followup.send(view=CV2("✅ Map Updated", "Coordinates updated."), ephemeral=True)
            else:
                await interaction.followup.send("Invalid coordinates format. Please enter in the format 'latitude, longitude'.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)

    async def enter_address(self, interaction: discord.Interaction):
        await interaction.response.send_message("Please enter the address:", ephemeral=True)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            address_msg = await self.bot.wait_for('message', check=check, timeout=60)
            address = address_msg.content
            self.coordinates = self.get_coordinates(address)
            if self.coordinates == (None, None):
                await interaction.followup.send("Failed to retrieve coordinates for the address. Please try again.", ephemeral=True)
            else:
                self.latitude, self.longitude = float(self.coordinates[0]), float(self.coordinates[1])
                self.location = address
                self.update_map()
                await self.update_embed(interaction)
                await interaction.followup.send(view=CV2("✅ Map Updated", "Address updated."), ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)


class MapStyleSelect(ui.Select):
    def __init__(self, map_view):
        super().__init__(placeholder='Select Map Style')
        self.map_view = map_view  
        options = [
            SelectOption(label='Map', value='map'),
            SelectOption(label='Satellite', value='sat'),
            SelectOption(label='Hybrid', value='hyb'),
            SelectOption(label='Light', value='light'),
            SelectOption(label='Dark', value='dark'),
        ]
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        print(f"Changing map style to {self.values[0]}")
        self.map_view.map_style = self.values[0]
        self.map_view.update_map()
        await self.map_view.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Map Updated", "Map style updated successfully."), ephemeral=True)

class MapSizeSelect(ui.Select):
    def __init__(self, map_view):
        super().__init__(placeholder='Select Map Size')
        self.map_view = map_view  
        options = [
            SelectOption(label='400x300', value='400,300'),
            SelectOption(label='800x600', value='800,600'),
            SelectOption(label='1200x900', value='1200,900')
        ]
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        print(f"Changing map size to {self.values[0]}")
        self.map_view.map_size = self.values[0]
        self.map_view.update_map()
        await self.map_view.update_embed(interaction)
        await interaction.response.send_message(view=CV2("✅ Map Updated", "Map size updated successfully."), ephemeral=True)


class Map(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="map", help="Shows a map of a location", usage="<location>", description="Shows a map of a location")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def map(self, ctx, *, location: str):
        view = MapView(self.bot, location, ctx)
        if view.coordinates == (None, None):
            await ctx.send(view=CV2("❌ Error", "Failed to retrieve coordinates for the location. Please try again."))
            return
        await ctx.send(view=view)

async def setup(bot):
    await bot.add_cog(Map(bot))
