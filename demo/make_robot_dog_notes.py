"""Generates a rambling, unstructured notes document about several fictional
robot dog prototypes -- realistic messy source material for exercising the
generator (FR-G1-G4): raw text in, formal patent sections out."""
from pathlib import Path

from docx import Document

OUT = Path(__file__).parent

PARAGRAPHS = [
    "Okay so I need to get all this written down before I forget it, we've been through like four "
    "prototypes now and my notes are scattered across three notebooks and a bunch of voice memos so "
    "here's the dump. Starting with Rex-4 since that's the one everyone keeps asking about.",

    "Rex-4 is the quadruped we built last spring, four legs obviously, each leg has three actuated "
    "joints (hip, knee, ankle if you want to call it that) driven by brushless motors with a planetary "
    "gearbox at each joint, maybe 6:1 reduction, I'd have to check the CAD again. The gait controller "
    "runs a trot pattern by default, diagonal leg pairs moving together, but we also hacked in a "
    "pace gait for low-traction surfaces like wet tile, and a crawl gait for when it's climbing over "
    "debris or stairs. Battery life on Rex-4 was honestly kind of bad, we were getting maybe 40 "
    "minutes of continuous walking before the pack dropped below the cutoff voltage, which is not "
    "great for a demo. The chassis is mostly 6061 aluminum with some 3D printed brackets that kept "
    "cracking at the ankle joint until we switched to nylon.",

    "Then there's Trotter, which honestly started as a joke name and it just stuck. Trotter is smaller "
    "than Rex-4, more of a desktop-companion size, maybe 30cm at the shoulder, and the big difference "
    "is we went with a different sensor suite. Rex-4 just had a front-facing depth camera and an IMU, "
    "but Trotter has the depth camera, a ring of six ultrasonic rangefinders around the body for "
    "near-field obstacle detection, and a microphone array so it can orient toward a sound, like if "
    "you call its name or clap. We also put a small inertial-stabilized camera gimbal on Trotter's "
    "head so the video feed doesn't bounce around when it's walking, which actually turned out to be "
    "one of the more popular features when we showed it to people, everyone commented on how smooth "
    "the video looked.",

    "Bark Unit Mk II (don't ask about Mk I, it doesn't really count, it never actually walked, it just "
    "sort of shuffled and fell over a lot) is the one with the modular leg attachment system, this is "
    "the one I'm most excited about honestly. The legs attach via a quick-release collar, kind of like "
    "a bayonet mount, so you can swap a standard walking leg for a wheel-leg hybrid, or a leg with a "
    "wider paw for soft sand, or even a leg with a little gripper claw on the end for manipulation "
    "tasks, picking things up off the floor, that kind of thing. We only ever built the walking legs "
    "and one wheel-leg prototype but the mount itself works, we tested the swap maybe fifty times and "
    "it held up fine mechanically. The wheel-leg thing is interesting because the leg can fold the "
    "wheel out of the way and walk normally on rough ground, then when it hits a smooth hallway it "
    "drops into a wheeled mode and just rolls, way more power efficient than walking on flat ground, "
    "we measured something like three times the distance per battery charge in wheel mode versus "
    "walking mode.",

    "Pogo is sort of the weird cousin of the family, it's a two-legged hopping robot rather than a "
    "quadruped, inspired by, well, honestly inspired by watching a kangaroo video at like 2am. Pogo "
    "has a single large actuator at the hip on each leg plus a passive spring element at the ankle "
    "that stores energy on landing and releases it on the next hop, so it's not fully active, part of "
    "the gait is just mechanical. Balance is the hard part obviously, we're using a reaction wheel in "
    "the torso to correct for lateral tipping and it mostly works but it still face-plants maybe one "
    "in ten hops if the surface has any slope to it. Not production ready at all, more of a research "
    "toy at this point, but the energy recovery numbers from the spring element were honestly better "
    "than I expected, something like 70% return.",

    "A few other things that cut across all of these that are worth writing down: we standardized on "
    "a shared power distribution board across Rex-4, Trotter, and Bark Unit Mk II, same connector "
    "pattern, so you can technically pull the battery pack off one and stick it on another, we did "
    "this by accident once when Trotter's pack died mid-demo and we grabbed Rex-4's pack off the "
    "shelf and it just worked, voltage and connector matched up fine. We also use the same base "
    "firmware across units with per-robot config files that set the leg count, actuator gear ratios, "
    "and gait tables, so the walking controller code itself doesn't really know or care which chassis "
    "it's running on, which has saved us a ton of duplicated work.",

    "On the sensor fusion side, all of them run some flavor of an extended Kalman filter combining the "
    "IMU data with leg odometry (basically dead-reckoning from the joint encoders and known leg "
    "geometry) to estimate body position and orientation, and whichever units have the depth camera "
    "also fold visual odometry into that estimate when lighting is good enough. In low light the "
    "visual odometry basically falls apart and we fall back to just IMU plus leg odometry, which "
    "drifts over time but is fine for short runs.",

    "Thermal is something we keep underestimating, the actuators on Rex-4 especially get hot after "
    "maybe fifteen minutes of continuous trotting, we added small heatsinks to the motor housings on "
    "the Mk II revision and that helped some but it's still the thing most likely to cause a thermal "
    "shutdown during a long demo. Something to actually design around properly next time instead of "
    "bolting on an afterthought.",

    "Also I keep forgetting to mention the paw design, we went through like six different paw "
    "materials, started with a hard rubber, then tried a silicone overmold with a lattice structure "
    "inside for some compliance, and the current favorite is a two-durometer design, firm core for "
    "load bearing with a softer rubber skin for grip, that one gave noticeably better traction on tile "
    "and less noise on hardwood, the hard rubber ones were honestly pretty loud, like a clicking sound "
    "every step which people found kind of unsettling actually.",

    "Anyway that's the brain dump, I'm sure I'm forgetting details, there's more in the voice memos "
    "about the Bark Unit Mk II gripper leg and the failed Mk I chassis but I think this covers the "
    "important stuff for now. We should probably pick one or two of these to actually push toward a "
    "real product instead of having four half-finished robots running around the lab.",
]

doc = Document()
for paragraph in PARAGRAPHS:
    doc.add_paragraph(paragraph)
doc.save(OUT / "robot_dog_notes.docx")
print(f"Wrote {OUT / 'robot_dog_notes.docx'}")
