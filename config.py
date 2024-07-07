

# Distance Matrix API (api that return the road distance between two address)
DM_URL = lambda origin, des: (f"https://api.distancematrix.ai/maps/api/distancematrix/json?"
                              f"origins={origin}&destinations={des}&key={DM_API_KEY}")
DM_API_KEY = "<API_KEY>"

DB_PATH = "db.json"
