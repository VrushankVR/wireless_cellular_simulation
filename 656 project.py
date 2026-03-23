import numpy as np
import matplotlib.pyplot as plt

# Parameters
Rcell = 1.5       # cell radius in km
fc = 900.0        # carrier freq MHz

Ptx = 10.0        # bs transmit power in watts
PtxdBm = 10*np.log10(Ptx*1000)

# improved test
Ptximproved = 40.0
PtxdBmimproved = 10*np.log10(Ptximproved*1000)

feederloss = 4.0     # feeder loss dB
Gtx = 8.0         # bs antenna gain dB
htx = 30.0        # bs height m
Nchannels = 50    # number of channels

Pmin = -102.0     # ms sensitivity dBm
Grx = 3.0         # ms antenna gain dB
Lbody = 3.0       # ms body loss dB
hrx = 1.5         # ms height m

callrate = 0.017  # average calls per min per user
calltime = 3*60   # call duration in seconds

shadowstd = 5.0   # shadowing standard deviation

dt = 1.0           # time step in seconds
minrequests = 100
scenariorepeat = 20

rng = np.random.default_rng(0)

# simple user placement in 2D
def placeusers(numusers):
    r = np.sqrt(rng.random(numusers))*Rcell
    r = np.clip(r, 0.01, None)
    angle = 2*np.pi*rng.random(numusers)
    x = r*np.cos(angle)
    y = r*np.sin(angle)
    return x, y, r

# shata path loss
def hataloss(dkm):
    f = fc
    hb = htx
    hm = hrx
    a = (1.1*np.log10(f) - 0.7)*hm - (1.56*np.log10(f) - 0.8)
    L = 69.55 + 26.16*np.log10(f) - 13.82*np.log10(hb) - a
    L = L + (44.9 - 6.55*np.log10(hb))*np.log10(dkm)
    return L

# scenario
def runone(numusers, txpower):
    # random distances inside circle
    x, y, r = placeusers(numusers)

    # path loss + shadowing
    loss = hataloss(r)
    loss = loss + rng.normal(0, shadowstd, numusers)

    # call state
    incall = np.zeros(numusers, dtype=bool)
    timeleft = np.zeros(numusers)

    # counters
    req = 0
    blk = 0
    start = 0
    drop = 0

    # link budget constant
    const = txpower + Gtx + Grx - feederloss - Lbody

    while req < minrequests:

        # fading
        fadepower = rng.exponential(1.0, numusers)
        fadedB = 10*np.log10(fadepower)

        # received powers
        Prx = const - loss + fadedB

        # check ongoing calls if dropped or finished
        for i in range(numusers):
            if incall[i]:
                if Prx[i] < Pmin:
                    incall[i] = False
                    timeleft[i] = 0
                    drop += 1
                else:
                    timeleft[i] -= dt
                    if timeleft[i] <= 0:
                        incall[i] = False
                        timeleft[i] = 0

        # count free channels
        used = np.sum(incall)
        free = Nchannels - used

        # new call attempts
        pcall = callrate*(dt/60.0)

        for i in range(numusers):
            if not incall[i]:
                if rng.random() < pcall:
                    req += 1

                    # low power block
                    if Prx[i] < Pmin:
                        blk += 1
                        continue

                    # no channel block
                    if free <= 0:
                        blk += 1
                        continue

                    # start call
                    incall[i] = True
                    timeleft[i] = calltime
                    start += 1
                    free -= 1

    return req, blk, start, drop

# simple 2D cell diagram
def plotcell(numusers):
    x, y, r = placeusers(numusers)
    plt.figure()
    plt.scatter(x, y, s=10)
    plt.scatter(0, 0, c="red", marker="x")
    ang = np.linspace(0, 2*np.pi, 200)
    cx = Rcell*np.cos(ang)
    cy = Rcell*np.sin(ang)
    plt.plot(cx, cy)
    plt.xlabel("x km")
    plt.ylabel("y km")
    plt.title("user placement in cell")
    plt.axis("equal")
    plt.grid()

# many users
def main():

    userlist = [10, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800]

    Pblockbase = []
    Pdropbase = []

    print("baseline 10 W:")
    for num in userlist:
        totreq = 0
        totblk = 0
        totstart = 0
        totdrop = 0

        for s in range(scenariorepeat):
            r, b, sr, d = runone(num, PtxdBm)
            totreq += r
            totblk += b
            totstart += sr
            totdrop += d

        Pblock = totblk/totreq
        Pdrop = totdrop/totstart if totstart > 0 else 0

        Pblockbase.append(Pblock)
        Pdropbase.append(Pdrop)

        print("NMS =", num,
              " Pblock =", round(Pblock,3),
              " Pdrop =", round(Pdrop,3),
              " req =", totreq,
              " start =", totstart,
              " drop =", totdrop)

    # improved power test
    Pblocknew = []
    Pdropnew = []

    print("improved system 40 W:")
    for num in userlist:
        totreq = 0
        totblk = 0
        totstart = 0
        totdrop = 0

        for s in range(scenariorepeat):
            r, b, sr, d = runone(num, PtxdBmimproved)
            totreq += r
            totblk += b
            totstart += sr
            totdrop += d

        Pblock = totblk/totreq
        Pdrop = totdrop/totstart if totstart > 0 else 0

        Pblocknew.append(Pblock)
        Pdropnew.append(Pdrop)

        print("NMS =", num,
              " Pblock =", round(Pblock,3),
              " Pdrop =", round(Pdrop,3),
              " req =", totreq,
              " start =", totstart,
              " drop =", totdrop)

    # find closest to 2% blocking in baseline
    target = 0.02
    bestnum = None
    bestdiff = 1.0
    for i in range(len(userlist)):
        diff = abs(Pblockbase[i] - target)
        if diff < bestdiff:
            bestdiff = diff
            bestnum = userlist[i]

    print("closest to 2 percent blocking:", bestnum,
          "with Pblock:", round(Pblockbase[userlist.index(bestnum)],3))

    # cell diagram
    plotcell(80)

    # final plots
    plt.figure()
    plt.plot(userlist, Pblockbase, marker="o", label="baseline")
    plt.plot(userlist, Pblocknew, marker="s", label="improved")
    plt.xlabel("number of MS")
    plt.ylabel("blocked call probability")
    plt.grid()
    plt.legend()
    plt.savefig("blocking_probability.png")

    plt.figure()
    plt.plot(userlist, Pdropbase, marker="o", label="baseline")
    plt.plot(userlist, Pdropnew, marker="s", label="improved")
    plt.xlabel("number of MS")
    plt.ylabel("drop probability")
    plt.grid()
    plt.legend()
    plt.savefig("dropping_probability.png")

    # plt.show()

main()
