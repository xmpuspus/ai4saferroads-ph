# LinkedIn draft

There is an ADB challenge running right now, "AI for Safer Roads." I didn't enter it, but I
spent a weekend on the problem and want to share what I found, in case it is a useful reference.

The clearest thing I found is also the most counterintuitive, and you can see it from space.

I built an open map that scores every drivable street in 51 Philippine cities against the speed
a person can actually survive a crash at, then folded in where people live (WorldPop) and where
they die (PSA road-death records). Three things you would expect to stack on top of each other
instead pull apart:

- The roads the map flags do run through the most crowded places. A flagged road has a median
  14,620 people per km² living around it, against 9,326 for a road whose limit already fits.
- But the size of the speed-limit gap does not track how crowded a place is. Crowding decides
  which roads get flagged, not how large the mismatch is.
- And the most crowded, most-flagged region, Metro Manila, has the country's lowest road-death
  rate: 3.6 per 100,000 against a national 10.9. The deadliest regions are rural (Cagayan Valley
  22.1, Caraga 16.9). Deaths are counted by where people live, dense cities have low free-flow
  speed and better trauma care, so the map of dangerous limits and the map of deaths point at
  different places.

On a satellite image the flagged corridors are obvious once you see them: a wide, fast road
posted 60 slicing through wall-to-wall low-rise housing, like Mel Lopez Boulevard through Tondo.
The limit was built for the road; the road was not built for the people beside it.

The method underneath is deliberately boring. For each of 357,423 streets, take a Safe System
survivable speed from the road's function and who is around it (30 km/h where people walk, 50 at
side-impact intersections, 70 on a divided carriageway), compare it to the posted limit from
OpenStreetMap, weight the gap by nearby schools, markets, transit and residents, and turn it into
stakes with the Nilsson power model (fatal risk scales with about the fourth power of speed, so
60 to 30 is roughly a 94% modeled cut). 7,586 streets carry a real posted limit above the
survivable speed.

A model is easy to fool, so I checked it against reality: 12,526 geolocated Metro Manila crashes
(2018-2020, from MMDA's public alerts) joined to the network. The flagged roads are 7% of the
network but carry 42% of the reported crashes, and crash density climbs with the score (Spearman
+0.35, p = 0.002). That is an association on a sample biased toward busy roads, not proof a limit
causes a crash, but the flags land where the crashes are.

And when I checked the thing people assume, that dangerous limits fall on poorer areas, the data
did not back it: across 43 cities the link is significant in only three, about what chance alone
produces.

Live map, method, validation, and the data are here: https://ai4saferroads-ph.vercel.app

Just a reference for anyone who needs it. Open code, open data, reproducible.
