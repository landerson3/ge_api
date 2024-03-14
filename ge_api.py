import requests, json, io, math, os
# import svg_draw
from PIL import Image, ImageDraw, ImageFont

class markup:
	def __init__(self, image: Image, markup_data: dict):
		self.image = image
		self.svg_data = markup_data
		self.w,self.h = self.image.size
		self.draw = ImageDraw.Draw(self.image)
		self.apply_markups()

	def apply_markups(self):
		for i,markup in enumerate(self.svg_data):
			self.markup = markup
			markup_colors = ['red','green','blue','orange','purple','black']
			self.markup_color = markup_colors[math.floor(i % len(markup_colors))]
			if 'svg' in markup:
				mu_item_1_props = markup['svg'][0]['properties']
				if len(mu_item_1_props['lines']) == 0: continue
				## write the text
				line_1 = mu_item_1_props['lines'][0]
				font_size =  (mu_item_1_props['fontSize'] / mu_item_1_props['onCreateCanvasHeight'])*self.h
				x1 = (line_1['x']/mu_item_1_props['onCreateCanvasWidth'])*self.w
				y1 = (line_1['y']/mu_item_1_props['onCreateCanvasHeight'])*self.h
				font = ImageFont.load_default(font_size)
				self.apply_text((x1,math.floor(y1*1.05)),font) # apply the text at the start of the markup
				for item in markup['svg']:
					self.apply_svg_outline_to_image(item) # <<< working from here; step through code and update
			else:
				font = ImageFont.load_default(self.h*.01)
				self.apply_text((self.w*.01, self.h*.01),font)

	def apply_text(self, loc: tuple, font):
		'''take an x,y coordinate and apply the name there'''
		name, userID = self.markup['name'], self.markup['userId']
		self.draw.text(loc, name, fill = self.markup_color, font = font)

	def apply_svg_outline_to_image(self, item):
		'''take a markup item and apply the lines to the destination image'''
		# Extracting relevant data from the dictionary
		lines = item['properties']['lines']
		# Create a draw object for the destination image
		
		# Draw the lines
		for i in range(len(lines)-1):
			x1 = (lines[i]['x']/item['properties']['onCreateCanvasWidth'])*self.w
			y1 = (lines[i]['y']/item['properties']['onCreateCanvasHeight'])*self.h
			x2 = (lines[i+1]['x']/item['properties']['onCreateCanvasWidth'])*self.w
			y2 = (lines[i+1]['y']/item['properties']['onCreateCanvasHeight'])*self.h	
			stroke_wid = math.floor((item['properties']['stroke']/item['properties']['onCreateCanvasWidth'])*self.w)
			self.draw.line((x1, y1, x2, y2), fill=self.markup_color, width=stroke_wid)
		return self.image
	
class ge_api:
	def __init__(self):
		self.api_key = 'Z7u0lYYQBq1B3kAwHjLYMaML84romC0laRgAvO7R'
		self.master_schema_id = 'e65500fc-1bb4-4beb-b319-ec6ff810af91'
		self.ret_input_collection = '361ef4cd-e045-4ddf-80d7-f38395039dff'
		self.account_user_id = '172497' ## account user ID
		self.integration_user_id = '158808'## integration user
		self.org_id = '171092'
		self.account_id = '171540'
		self.user_id = self.integration_user_id
		self.set_auth_headers()
		self.set_user_id(self.integration_user_id) 
		self.scopeType = 'workspace'
		self.scopeID = self.account_id

	def set_user_id(self,user_id):
		self.user_id = 	user_id
		self.auth_headers['x-globaledit-userid'] = self.user_id
		# self.scopeID = self.user_id

	def set_auth_headers(self):
		self.auth_headers = {
			'x-globaledit-api-key': self.api_key,
			'x-globaledit-userid': self.user_id,
			'Accept': 'application/json'
		}
		
	def get_workspace_folders(self, workspace_id):
		response = requests.get(f'https://dev.globaledit.com/v1/users/workspaces/{workspace_id}/folders', headers = self.auth_headers)
		return json.loads(response.content)

	def get_collection_assets(self, collection_id) -> list:
		'''take a collection_id and return a list of asset objects'''
		response = requests.get(f'https://dev.globaledit.com/v1/collections/{collection_id}/assets', headers = self.auth_headers)
		if response.status_code < 300:
			r = json.loads(response.content)
			if 'assets' in r:
				return r['assets']

	def get_user_collections(self, user_id = None):
		headers = self.auth_headers
		if user_id != None:
			headers['x-globaledit-userid'] = user_id
		response = requests.get(f"https://dev.globaledit.com/v1/accounts\
			/{self.account_id}/collections", headers = headers)
		return json.loads(response.content)

	def get_metadata_schemas(self):
		url = f'https://dev.globaledit.com/v1/metadata/schemas?\
				accountId={self.account_id}&scopeType={self.scopeType}&scopeId={self.scopeID}'
		response = requests.get(url, headers = self.auth_headers)
		return json.loads(response.content)

	def get_metadata_values(self, asset_ids: list|tuple, schemaId: str|int = None):
		if schemaId == None: schemaId = self.master_schema_id
		body = json.dumps({
			'assetIDs':list(asset_ids)
		})
		headers = self.auth_headers
		headers['Content-Type'] = 'application/json'
		url = f'https://dev.globaledit.com/v1/metadata/{schemaId}?scopeType={self.scopeType}&scopeId={self.scopeID}'
		response = requests.post(url, headers = headers, data = body)
		return json.loads(response.content)

	def get_asset_markup(self, asset: dict) -> dict:
		'''take an asset object and return the markup as a json object
		see https://api-docs.globaledit.com/#556eb6b9-7a09-47cd-90c8-250a6a10f026:~:text=Get%20Asset-,Markup,-GET
		'''
		url = f"https://dev.globaledit.com/v1/assets/{asset['id']}/markups/?scopeType=collection&scopeId={self.ret_input_collection}"
		response = requests.get(url, headers=self.auth_headers)
		return json.loads(response.content)

	def get_original_asset(self, asset: dict) -> Image:
		asset_id = asset['id']
		url = f"https://dev.globaledit.com/v1/files/assets/{asset_id}/originals?scopeType=workspace&scopeId={self.scopeID}"
		response = requests.get(url, headers=self.auth_headers)
		im = Image.open(io.BytesIO(response.content))
		return im

	def get_markup_image(self, asset, *image):
		# takes an asset, gets the image, adds the markups
		data = self.get_asset_markup(asset)
		if image == None or image == ():
			image = self.get_original_asset(asset)
		mu = markup(image, data)
		return mu.image
		
	def get_preview_image(self, asset, size:int = 1280) -> Image:
		avail_sizes = [80 , 135, 280, 1280, 3072]
		if size not in avail_sizes:
			# select the closest size
			m_size = None
			size_diff = None
			for s in avail_sizes:
				if size - s < size_diff:
					m_size = s
					size_diff = size - s 
			size = m_size
		
		headers = self.auth_headers
		if 'Accept' in headers:
			del(headers['Accept'])
		url = f"https://dev.globaledit.com/v1/files/assets/{asset['id']}/previews/{size}/?scopeType=workspace&scopeId={self.scopeID}"
		response = requests.get(url, headers=headers)
		if response.status_code < 300:
			im = Image.open(io.BytesIO(response.content))
			return im
		


	


g = ge_api()
# folders = g.get_workspace_folders('171573')

assets = g.get_collection_assets(g.ret_input_collection)

for i,asset in enumerate(assets):
	preview_image = g.get_preview_image(asset,1280)
	mark_up_image = g.get_markup_image(asset)
	mark_up_image.save(os.path.expanduser(f"~/Desktop/{asset['name']}"))
	if i > 5: break
