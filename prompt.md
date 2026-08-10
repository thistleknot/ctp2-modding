Map Reduce Schma translation
	the problem with agentic ai is you have to babysit it one task implementation at a time.  which seems to be counterintuitive.  I'm sure it's lack of model capabilitiy and/or agentic harness.  but gpt-5.5 seemed to handle tasks fairly well.  I started from the basics and defined a dimensional schema based on what could be modded, and items individual expressions of that dimension as records, and then from here, everything started to fall into place as I could map between civ2 and ctp2.  The next piece was image parsing with all their individual formats between the files, but that's been setup as a set of parsing tools.  And I intend to route everything through a single python wrapper for cli patching in former civ2 mods (that's what I'm aiming for, auto ingest a total conversion mod as a scenario).  This was all made possible when I decided to drop patching manually with an llm to formalizing schema contract translation layer 
	i went back to the basics. diff ae mod to the following ctp2 mods individiually: lotr, cradles, ages of man
	from there I had a ctp2 schema
	then I did the same for base civ2 (test of time edition) to momjr, mars, and heroes of might and magic
	always try to do a 3 way comparison.
	for slic, I documented file: class/function headers, constant labels
	and then let an llm transpose civ2 events as slic


I went through what was missing between our civ2/ctp2 schema mapping and thought... why didn't we identify tile improvements in civ2, because they have them, why not leaders in ctp2 because we have those.  So I wrote them out for what was claimed as missing (provided the civ2 leaders and ctp2 tile improvements).  I think we need to identify and update our list of dimensions and their records and find them where they exist in files and include at a high level readme those files because they are 1st class citizens (txt file and image files) alongside the counts we mapped . i.e. teh counts in dimension_inventory.md

Note: I'm not really sure how events should translate, idk if they are simply tied to epochs (ages)

civ2 mods
	 - [observed] H:\games\civ2\SCENARIO\MOMJR\RULES.TXT defines native sections @CIVILIZE, @IMPROVE, @ENDWONDER, @UNITS, @TERRAIN, @GOVERNMENTS, @LEADERS, @CARAVAN, @ORDERS, plus tuning sections like @COSMIC, @DIFFICULTY, @ATTITUDES.
	 - [observed] In Civ2 MOMJR, wonders are not a separate primary table; they live inside @IMPROVE, with @ENDWONDER supplying the expiration mapping.
	 - [observed] In the CTP2 MoM toolchain, the explicit full-kit surfaces are advances, units, buildings/improvements, wonders, terrain, goods, tileimp, governments, orders, concepts, scenario_art, with sidecars like icons and movies.
	 - [syllogism] So the translation should not assume Civ2 and CTP2 have the same dimension boundaries; some CTP2 dimensions are splits of a single Civ2 surface.

		Civ2 MOMJR native dimensions

			 1. Advances
			 2. City improvements
			 3. Wonders as a subtype of improvements, not a separate dimension
			 4. Units
			 5. Terrain
			 6. Governments
			 7. Leaders / personalities
				Americans
				Arabs
				Aztecs
				Babylonians
				Carthaginians
				Celts
				Chinese
				Egyptians
				English
				French
				Germands
				Greeks
				Incas
				Indians
				Japanese
				Mongols
				Persians
				Romans
				Russians
				Sioux
				Spanish
				Vikings
				Zulus
			 8. Caravan commodities / trade lane data
			 9. Orders / command text
			 10. Events
			 11. Civilopedia / labels / game text
			 12. Scenario art sheets and sounds
			 
			 13. Tile
				Airbase
				FArmland
				Fortress
				Immigration
				Mine
				Pollution
				Railroad
				Roads

		CTP2 MoM full-kit dimensions

			 1. Advances
			 2. Units
			 3. City Improvements / Buildings
			 4. Wonders
			 5. Terrain
			 6. Goods
			 7. Tile Improvements
				see dimension_inventory.md

					### Tile_Improvements {81}
					- source: `tile_improvements.csv`
					- `TILEIMP_ADVANCED_FARMS`
					- `TILEIMP_ADVANCED_MINES`
					- `TILEIMP_ADVANCED_UNDERSEA_MINES`
					- `TILEIMP_AIR_BASEs`
					- `TILEIMP_AIR_BASES`
					- `TILEIMP_AUTOMATED_FISHERIES`
					- `TILEIMP_DRILLING_PLATFORM`
					- `TILEIMP_FARMS`
					- `TILEIMP_FISHERIES`
					- `TILEIMP_FORTIFICATIONS`
					- `TILEIMP_HYDROPONIC_FARMS`
					- `TILEIMP_LISTENING_POSTS`
					- `TILEIMP_MAGLEV`
					- `TILEIMP_MEGA_MINES`
					- `TILEIMP_MEGA_UNDERSEA_MINES`
					- `TILEIMP_MINES`
					- `TILEIMP_NATURE_PRESERVE`
					- `TILEIMP_NETS`
					- `TILEIMP_OUTLET_MALL`
					- `TILEIMP_PORT`
					- `TILEIMP_PROCESSING_TOWER`
					- `TILEIMP_RADAR_STATIONS`
					- `TILEIMP_RAILROAD`
					- `TILEIMP_ROAD`
					- `TILEIMP_RUINS`
					- `TILEIMP_SONAR_BUOYS`
					- `TILEIMP_TERRAFORM_BROWN_HILL`
					- `TILEIMP_TERRAFORM_BROWN_MOUNTAIN`
					- `TILEIMP_TERRAFORM_DESERT`
					- `TILEIMP_TERRAFORM_FOREST`
					- `TILEIMP_TERRAFORM_GRASSLAND`
					- `TILEIMP_TERRAFORM_HILL`
					- `TILEIMP_TERRAFORM_JUNGLE`
					- `TILEIMP_TERRAFORM_MOUNTAIN`
					- `TILEIMP_TERRAFORM_PLAINS`
					- `TILEIMP_TERRAFORM_SWAMP`
					- `TILEIMP_TERRAFORM_WHITE_HILL`
					- `TILEIMP_TERRAFORM_WHITE_MOUNTAIN`
					- `TILEIMP_TRADING_POST`
					- `TILEIMP_UNDERSEA_MINES`
					- `TILEIMP_UNDERSEA_TUNNEL`
			 8. Governments
			 9. Unit Orders
			 10. Concepts
			 11. SLIC
			 12. Scenario Art
			 
			 13. Civilizations
				Americans
				Assyrian
				Australian
				Barbarians
				Brazilian
				Canadian
				Chinese
				Cuban
				Dutch
				Egyptian
				English
				Ethiopian
				French
				German
				Greek
				Hebrew
				Incan
				Indonesian
				Irish
				Japanese
				Korean
				Mayan
				Mexican
				Mongol
				Native American
				Nicaraguan
				Nigerian
				Peresian
				Phoneician
				Polish
				Polynesian
				Portuguese
				Roman
				Russian
				Scottish
				Spanish
				Thai
				Turkish
				Viking
				Welsh
				Zulu
				
				[AE] (also considered part of baseline by my definition)
				Aboriginal
				Arabian
				Argentinian
				Aermenian
				Austrian
				Babylonian
				Byzantine
				Carthaginian
				Celtic
				Etruscan
				Han
				Harappan
				Hittite
				Italian
				Jamaican
				Khmer
				Kurdish
				Kushite
				Lycian
				Macedonian
				Malian
				Minoan
				Nubian
				Shang
				Slavic
				Sumerian
				Swedish
				Yamato
			
			civ2		ctp2
			Advances		Advances
			Units		Units
			City improvements		City Improvements / Buildings
			Wonders as a subtype of improvements, not a separate dimension		Wonders
			Terrain		Terrain
			Caravan commodities / trade lane data		Goods
					Tile Improvements
			Governments		Governments
			Orders / command text		Unit Orders
			Leaders / personalities		
			Events		SLIC
			Civilopedia / labels / game text		Concepts
			Scenario art sheets and sounds		Scenario Art

	I wanted to treat some items as 'keep' if they are genre agnostic, else only mom

## Civ2 Count Matrix

| Mod | advances | governments | improvements | leaders | terrain | tile_improvements | units | wonders |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 100 | 7 | 38 | 21 | 33 | 8 | 63 | 29 |
| momjr | 100 | 7 | 38 | 23 | 33 | 8 | 62 | 29 |
| moojr | 93 | 7 | 38 | 23 | 33 | 8 | 62 | 29 |

## CTP2 Current Full-Kit Count Matrix

| Mod | advances | civilizations | concepts | goods | goods_icons | goods_ids | government_icons | governments | improvements | orders | terrain | terrain_icons | tile_improvements | units | wonder_icons | wonder_movies | wonders |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mom | 100 | 75 | 61 | 72 | 17 | 82 | 5 | 5 | 68 | 47 | 26 | 24 | 81 | 62 | 36 | 30 | 30 |

## CTP2 Reference Roundtrip Count Matrix

| Mod | advances | unit_icons | units | wonders |
| --- | --- | --- | --- | --- |
| ae | 107 | 546 | 72 | 30 |
| aom | 211 | 951 | 286 |  |
| base | 107 |  | 74 |  |
| cradle | 281 | 939 | 198 |  |
| lotr | 333 |  | 214 |  |
