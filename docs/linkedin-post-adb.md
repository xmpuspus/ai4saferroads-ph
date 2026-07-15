# LinkedIn post (ADB template version)

## Post body

I saw this competition ADB posted a while back (link's in the comments). It's basically supposed to get cities to use AI and data to figure out where their speed limits are set wrong, Metro Manila included. I didn't join but it did pique my interest. The goal was to set the right speed limits, but I wanted to push it a bit further. Is it really slow speed limits that keep us safe?

So I dug into it and found out that basically... it's not an easy or direct answer. I mean enforcement is obviously the first fix, and we're honestly not very good at that. But then a few more findings kind of messed with my head.

Turns out on EDSA, the crashes at 3am, when the road finally clears up, are twice as likely to injure or kill as the ones in rush hour. Which is kind of nuts. It's not the traffic that gets you, traffic actually keeps everyone slow. It's the moment the road empties out and cars finally hit the speed it was really built for.

And when I looked at the flagged roads from satellite, they basically all look the same. Super wide, dead straight, like ten lanes, cutting right through where people live. EDSA, Taft, Commonwealth, that new Davao coastal road. Nobody's doing 60 on a road built to move way faster than that.

Then I dropped 12,563 real crashes onto my map, and the roads I flagged are only 8.5% of the total road length but carry 76% of the crashes. So it's landing right where people actually get hurt. And the uncomfortable part is the fix was never really the sign. It's the road itself. Humps, narrower lanes, proper crossings, the stuff that slows you down even when it's empty.

But here's where I kept getting stuck. You can't exactly put speed humps on EDSA. The roads carrying the most crashes are usually the big ones you can't really reshape, they have to keep traffic moving. So you can't fully blame the shape of the road either, "fix the road" kind of breaks down on the exact roads that need it most. And even the ones you could fix, only 20% of Manila's flagged roads have anything like that within 100m. In Davao it's 4%.

So yeah, is speed the problem? Kind of. But it's the top speed the road lets cars hit near people, not the crawl you're stuck in right now. And for the big roads you can't physically fix, this is exactly where it would've been nice if enforcement and good governance actually kicked in. Cameras that work, consequences that stick, someone actually running the thing. That's the part that would make everyone safer. Not slapping a lower number on a sign nobody follows anyway.

And honestly, you could say most of this is just common sense, pretty self-explanatory once you actually look at it. But having the data back it up is still kind of validating.

Funny enough I ended up basically building the thing the challenge was asking for anyway, a speed safety score on a map, just because I couldn't let it go. Every drivable street across 50 cities and Metro Manila, the current limit against the speed you'd actually survive.

The comments have all the data and references I had to study. Attached is a quick view of what I found.

So maybe it was never really about the limit, or even the road. Maybe we just never got around to enforcing or fixing either one.

## Hashtags

#RoadSafety #VisionZero #DataForGood #CivicTech #UrbanMobility #AI #OpenData #Philippines

## First comment (post this yourself, right after publishing)

The map, open and no login
https://ai4saferroads-ph.vercel.app

The ADB challenge that set me off
https://challenges.adb.org/en/challenges/ai4saferroads

How it is built, every threshold and formula
https://ai4saferroads-ph.vercel.app/methodology

Code and data, open source
https://github.com/xmpuspus/ai4saferroads-ph

What I studied

Road network and speed limits, from OpenStreetMap
https://www.openstreetmap.org

EDSA crash severity by hour, MMDA records 2007 to 2016 (22,072 crashes), published on Mendeley by Luz and Blanco, UP Diliman
https://data.mendeley.com/datasets/hwbf6n4krw/1

Crash locations for the 76% on 8.5% check, MMDA traffic-alert mirror 2018 to 2020 (12,563 with coordinates)
https://github.com/PotatoC0der/mmda_traffic_analysis

Survivable speeds, from Tingvall and Haworth 1999 (Vision Zero), the ITF and OECD Speed and Crash Risk 2018, and the WHO Speed Management Manual
https://www.monash.edu/muarc/archive/our-publications/papers/visionzero
https://www.itf-oecd.org/speed-crash-risk
https://www.who.int/publications/m/item/speed-management--a-road-safety-manual-for-decision-makers-and-practitioners

Fatal risk against speed, from the Nilsson power model (2004) and Tefft 2011 pedestrian survival curves (AAA Foundation)
https://portal.research.lu.se/en/publications/traffic-safety-dimensions-and-the-power-model-to-describe-the-eff/
https://aaafoundation.org/impact-speed-pedestrians-risk-severe-injury-death/

Road shape from above, from Esri World Imagery (Esri, Maxar, Earthstar Geographics)
https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9

Who lives around each road, from WorldPop 2020 (Philippines, 100m)
https://hub.worldpop.org/geodata/summary?id=6316

A flag means a road is worth reviewing, not that the limit is definitely wrong. These are statistical indicators from public data and patterns can have legitimate explanations. Not affiliated with ADB, WHO, or iRAP.

## Attach
docs/demo.gif (the 15-second red map cut). Static alternative: build/web/og-card.png.
