from itertools import combinations
import phoenixAES
from tqdm import tqdm

# ik10: ....D640..350C..4F2F....B2....D0
#  1: 50f8fa94169b0aac172d53af935d3f39
#     ....D640..350C..4F2F....B2....D0
#  2: 1e8de8480816e2e41f3bb14b8c668e72
#     ....D640..350C..4F2F....B2....D0
#  3: 2994a82c21824ac83eb9fb83b2df75f1
#     ....D640..350C..4F2F....B2....D0
#  4: bf09091b9e8b43d3a032b85012edcda1
#     ....D640..350C..4F2F....B2....D0
#  5: fab43bd2643f7801c40dc051d6e00df0
#     ....D640..350C..4F2F....B2....D0
#  6: 3b63b7245f5ccf259b510f744db10284
#     ....D640..350C..4F2F....B2....D0
#  7: b314e8c7ec4827e2771928963aa82a12
#     ....D640..350C..4F2F....B2....D0
#  8: f1f121471db906a56aa02e3350080421
#     ....D640..350C..4F2F....B2....D0
#  9: da03dc14c7badab1ad1af482fd12f0a3
#     ....D640..350C..4F2F....B2....D0
# 10: 258fd640e2350cf14f2ff873b23d08d0
#     ....D640..350C..4F2F....B2....D0

# 100%|█████████████████████████████████████████████████████████████████████████████| 65535/65535 [16:43<00:00, 65.31it/s]
# 258fd640e2350cf14f2ff873b23d08d0
# None 881
# ......40....0C....2F....B2...... 294
# ....D6....35....4F............D0 3822
# ..8F....E2............73....08.. 3150
# 25............F1....F8....3D.... 1134
# ....D640..350C..4F2F....B2....D0 1274
# ..8F..40E2..0C....2F..73B2..08.. 1050
# 25....40....0CF1..2FF8..B23D.... 378
# ..8FD6..E235....4F....73....08D0 13650
# 25..D6....35..F14F..F8....3D..D0 4914
# 258F....E2....F1....F873..3D08.. 4050
# ..8FD640E2350C..4F2F..73B2..08D0 4550
# 25..D640..350CF14F2FF8..B23D..D0 1638
# 258F..40E2..0CF1..2FF873B23D08.. 1350
# 258FD6..E235..F14F..F873..3D08D0 17550
# 5601DDB67D6DC7FD64711EE0E000F443 5850


good_faults = [
    bytes.fromhex('4b26bf7cbb2f866d7ec8227a7ce955f0'),
    bytes.fromhex('4b26bfc9bb2f5f6d7e05227a03e955f0'),
    bytes.fromhex('4b264f29bbf4566dda79227ae2e955de'),
    bytes.fromhex('4b266829bb0f566dec79227ae2e955fb'),
    bytes.fromhex('4b04bf29762f566d7e79226ce2e9b7f0'),
    bytes.fromhex('0726bf29bb2f56c57e79237ae28d55f0'),
    bytes.fromhex('4b9cbf29302f566d7e7922b3e2e964f0'),
    bytes.fromhex('4b88bf295a2f566d7e79221de2e9cdf0'),
    bytes.fromhex('4b26be29bb7d566de379227ae2e955a0'),
    bytes.fromhex('4b04bf29762f566d7e79226ce2e9b7f0'),
    bytes.fromhex('4b268229bb8c566d3679227ae2e955d3'),
    bytes.fromhex('9c26bf29bb2f564c7e796e7ae28c55f0'),
    bytes.fromhex('4bd8bf29682f566d7e79221be2e9e9f0'),
    bytes.fromhex('9c26bf29bb2f564c7e796e7ae28c55f0'),
    bytes.fromhex('4b26fa29bb7b566db079227ae2e95515'),
    bytes.fromhex('0726bf29bb2f56c57e79237ae28d55f0'),
]

refout = bytes.fromhex('4b26bf29bb2f566d7e79227ae2e955f0')

big_list = []
for n in range(1, len(good_faults)+1):
    big_list += list(combinations(good_faults, n))

print(len(big_list))

options = {}

for idx,l in enumerate(tqdm(big_list)):
    ik10 = phoenixAES.crack_bytes(l, refout, lastroundkeys=[], encrypt=True, outputbeforelastrounds=True, verbose=1)
    # print(f'ik{10}: {ik10}')
    try:
        options[ik10] += 1
    except KeyError:
        options[ik10] = 1
    
    if idx % 500 == 0:
        print('258FD640E2350CF14F2FF873B23D08D0')
        for k,v in options.items():
            print(k,v)

print('258FD640E2350CF14F2FF873B23D08D0')
for k,v in options.items():
    print(k,v)
