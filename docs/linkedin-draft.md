# LinkedIn draft

I have sat in enough EDSA traffic to have had the thought everyone has. The limit is 60, traffic
keeps us under 30, and people still die on this road. So how is speed even the problem?

There is an ADB challenge running now, "AI for Safer Roads." I did not enter it, but that
question stuck with me, so I spent a weekend trying to answer it honestly. If we never reach the
limit, why would the limit matter.

First I had to find crash data that could actually answer it. Most of what is public is just dots
on a map, no severity, no time, which cannot tell a fender-bender from a fatality. The one open
Philippine set I could find that can is MMDA's EDSA crash records, published by University of
the Philippines researchers, 22,072 crashes from 2007 to 2016,
each with a severity and a timestamp. So I ran the split.

Here is what surprised me. The obvious story is wrong. Crashes do not pile up at night when the
road is empty. They peak in the morning rush, with the traffic, because more cars means more
crashes. If I had gone with my gut and posted "crashes happen at night," the data would have
embarrassed me.

But total crashes are not deaths. When I split by severity it flipped. The share of crashes that
injure or kill roughly doubles late at night. That is when EDSA finally clears and cars reach the
speed the road is built for. 13.5 percent from midnight to 5am, against 6.7 percent in the rush hour.
Same road, twice as deadly per crash, when it is empty. Traffic produces the fender-benders. The
clear road produces the casualties.

I want to be honest about the limits of that. It is one road, EDSA. Those late-night hours bring less
enforcement and more drinking, so it points to speed, it does not prove it alone. There are only 22
fatal crashes in the whole set, too few to read hour by hour, so I measured injuries and deaths
together instead of deaths alone.

One thing the night does not muddy is the shape of the road. OpenStreetMap has no width for most of these
streets, so I looked from space instead. The flagged roads all look the same. Wide, dead
straight, many lanes, cutting through wall-to-wall housing. EDSA at ten-plus lanes. Taft under the
LRT with homes at the kerb. The new Davao coastal road running past informal settlements. This is
not reckless drivers. The road is built for a speed no sign changes, and that is the speed it
delivers the moment it clears.

Then I checked it against reality. I dropped 12,563 reported Metro Manila crashes onto the scored
map. The roads I flag are 7 percent of the street length and carry 42 percent of the crashes. The
flags land where people actually get hurt.

The fix is the uncomfortable part. A lower number on a sign nobody obeys and nobody enforces
changes nothing. What actually works is physical. A road built so you cannot speed even when it is
empty. Humps, narrowing, raised crossings. Yet only 21 percent of Manila's flagged roads have
any of that within 100 meters. In Cebu it is 10 percent. In Davao, 4.

So the answer to the objection is yes, speed is the problem, just not the average speed. What
puts you in danger is the top speed the road lets cars reach near you, however slow the traffic
is right now. I put the whole thing on an open
map, every drivable street in 51 Philippine cities, the current limit against the speed a person
survives, with the real crashes laid over the satellite so you can see it for yourself.

Is it the limit that is wrong, or the road we built underneath it?

[attach docs/demo.gif]
