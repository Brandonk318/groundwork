RESOURCES = [
 {"id":"r1","name":"Texas Legal Aid (example listing)","category":"legal_aid","description":"General legal information and referrals. Not legal advice.","phone":"","url":""},
 {"id":"r2","name":"Treatment locator (SAMHSA FindTreatment)","category":"treatment","description":"Substance-use treatment referrals.","phone":"","url":"https://findtreatment.gov"},
 {"id":"r3","name":"Public transit trip help","category":"transit","description":"Bus and transit information.","phone":"","url":""},
 {"id":"r4","name":"Counseling referral desk","category":"treatment","description":"Counseling referrals for people in recovery.","phone":"","url":""},
]
MEETINGS = [
 {"id":"m1","name":"Morning Serenity AA","program":"AA","day":"Monday","time":"07:00","city":"Fort Worth","address_public":"Community center, Fort Worth","lat":32.7555,"lng":-97.3308,"online":False},
 {"id":"m2","name":"Evening Hope NA","program":"NA","day":"Tuesday","time":"19:00","city":"Fort Worth","address_public":"Church hall, Fort Worth","lat":32.76,"lng":-97.34,"online":False},
 {"id":"m3","name":"Online SMART Recovery","program":"SMART","day":"Wednesday","time":"18:00","city":"Online","address_public":"Online meeting","lat":None,"lng":None,"online":True},
]
JOBS = [
 {"id":"j1","title":"Roofing helper","company":"Second-chance roofing contractor (example)","location":"Fort Worth, TX","second_chance":True,"description":"No state license required. Check parole conditions with your officer before applying.","trade":"roofing"},
 {"id":"j2","title":"Warehouse associate","company":"Fair-chance employer (example)","location":"Dallas, TX","second_chance":True,"description":"Entry level. Background-friendly hiring pledge.","trade":"warehouse"},
 {"id":"j3","title":"Landscaping crew member","company":"Local landscaping (example)","location":"Fort Worth, TX","second_chance":True,"description":"No state license required. Check parole conditions with your officer.","trade":"landscaping"},
]
VENUE_STOPS = ["entrance","zero-proof bar","lounge","stage","dining"]
# SAMPLE ONLY: placeholder directory rows so the UI has shape. NOT real listings.
COMMUNITY_GROUPS = [
 {"id":"g1","name":"Sample Recovery Circle","kind":"recovery","city":"Fort Worth","meeting_time":"Saturday 10:00","sample":True},
 {"id":"g2","name":"Sample Reentry Support Night","kind":"reentry","city":"Dallas","meeting_time":"Thursday 18:30","sample":True},
 {"id":"g3","name":"Sample Community Church Gathering","kind":"faith","city":"Fort Worth","meeting_time":"Sunday 11:00","sample":True},
]
MUSIC_TRACKS = [
 {"id":"t1","title":"Sample Track One","artist":"Sample artist","sample":True,"src":"sample:t1"},
 {"id":"t2","title":"Sample Track Two","artist":"Sample artist","sample":True,"src":"sample:t2"},
]
HOUSING_PLAN_STEPS = [
 {"id":"hp1","title":"Gather ID and documents","pointer":"211 can point to local document help."},
 {"id":"hp2","title":"Track income and monthly budget","pointer":"Use the savings tracker here; figures are yours."},
 {"id":"hp3","title":"Build a savings goal for deposits and fees","pointer":"Set a goal below; no invented figures."},
 {"id":"hp4","title":"Line up references","pointer":"Ask a mentor, employer, or faith leader you trust."},
 {"id":"hp5","title":"Call 211 for local housing resources","pointer":"Groundwork does not provide housing or partner with providers."},
]
