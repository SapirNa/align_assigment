import uvicorn
import geocoder
from geopy import distance
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB, Query

from config import DB_PATH

app = FastAPI()


class Mission(BaseModel):
    agent: str
    country: str
    address: str
    date: str


class Target(BaseModel):
    target_location: str


@app.post("/mission")
def post_mission(mission: Mission) -> None:
    """
    Get mission details from user and add to TinyDB - local json file
    """
    db = TinyDB(DB_PATH)
    db.insert({"agent": mission.agent,
               "country": mission.country,
               "address": mission.address,
               "date": mission.date})

    db.close()


@app.get("/countries-by-isolation")
def get_most_isolated_country() -> str:
    """
    Find the country with the highest degree of isolated agents from DB.
    :return: country name
    """
    db = TinyDB(DB_PATH)
    all_agents = [mission["agent"] for mission in db]
    unique_agents = [agent for agent in all_agents if all_agents.count(agent) == 1]

    countries = []
    for agent in unique_agents:
        mission_data = db.get(Query()["agent"] == agent)
        countries += [mission_data["country"]] if mission_data else []

    db.close()
    try:
        return max(set(countries), key=countries.count)

    except ValueError:
        raise HTTPException(status_code=500, detail="The Database is empty, please enter missions")


@app.post("/find-closest")
def find_closest_mission(target: Target) -> dict:
    """
    Find the closest mission from a specific address by aerial distance (without considering the roads)
    :param target: target address or geo coordinates
    """
    target_location = target.target_location
    db = TinyDB(DB_PATH)

    if not db.all():
        raise HTTPException(status_code=500, detail="The Database is empty, please enter missions")

    target_cord = geocoder.arcgis(location=target_location)
    minimal_distance = -1

    for mission in db:
        mission_cord = geocoder.arcgis(location=f"{mission['address']}, {mission['country']}")
        dis = distance.distance(tuple(mission_cord.latlng), tuple(target_cord.latlng)).km

        if minimal_distance == -1 or dis < minimal_distance:
            minimal_distance = dis
            closest_mission = mission

    return {"distance": "{:.2f} km".format(minimal_distance), "mission": closest_mission}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
