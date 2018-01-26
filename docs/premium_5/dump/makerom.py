import os

# Sample #5 "SOFTWARE 23" BEETLE
ffs = ['00AF', '0163', '02C3', '02E6', '02E7', '0302', '0821', '09BE', '09D8', '0AA4', '0B22', '0B27', '0B51', '0EF6', '1313', '1431', '148B', '15F3', '15F6', '1749', '17ED', '1B7D', '1BE2', '1C26', '1C59', '1DFC', '2017', '20F4', '210B', '211A', '221F', '2759', '275A', '28AC', '2974', '2995', '29AC', '29FC', '2A38', '2CFB', '30DB', '311F', '3193', '320F', '36EA', '3908', '3981', '3BD2', '3D21', '3ED3', '3ED8', '42A2', '42A4', '43AD', '4645', '484B', '49D5', '4A01', '4A08', '4AAA', '4AD6', '4ADD', '4B7E', '4BCD', '4C20', '4C4C', '4C53', '4C72', '4CAA', '4CD9', '4CE2', '4E1C', '51AB', '5617', '5628', '56A5', '5746', '5772', '597A', '59E6', '59E7', '5A9C', '5B3B', '5C82', '5CB5', '5D67', '5D7D', '6223', '6228', '62F7', '6300', '630E', '6335', '6339', '6348', '67BF', '67D5', '67D7', '6842', '698D', '699B', '6A25', '6A27', '6A32', '6A5F', '6A61', '6A7D', '6A84', '6A9F', '6AB1', '6AB8', '6ABF', '6ACD', '6AF6', '6B05', '6B09', '6B10', '6B19', '6B22', '6B2B', '6B34', '6B3F', '6B49', '6B6C', '6B7D', '6B93', '6BA0', '6BF1', '6BFF', '6C16', '6C2F', '6C45', '6C5E', '6C83', '6C8F', '6DAD', '6DF8', '6E3B', '6EA9', '7037', '7047', '707E', '70A2', '7106', '712B', '7130', '7155', '7177', '7180', '71A8', '71B1', '71C7', '71D0', '71EE', '71FD', '721F', '7221', '7236', '7244', '7246', '7252', '7260', '7262', '726A', '7297', '72E4', '72EF', '7306', '7310', '734C', '7357', '738A', '73A6', '73D5', '73DE', '73E0', '73E4', '73FB', '743D', '7442', '744D', '748E', '7493', '749E', '74C6', '74CB', '74D9', '74EA', '7536', '7580', '75D4', '75EC', '7601', '7621', '7639', '764E', '76BB', '76C6', '79B2', '7B61', '7C5E', '7D6D', '7DDD', '7E1E', '7F05', '7F6F', '80F4', '884D', '89B2', '89B5', '90B0', '90B3', '9531', '98DC', 'A041', 'A044', 'A187', 'A1D5', 'A1D8', 'A4F4', 'A5A0', 'A618', 'A63F', 'A659', 'A84D', 'A85C', 'A8BC', 'A8CC', 'A9B9', 'A9EA', 'AA3C', 'AB70', 'ABA1', 'ABAA', 'ABE2', 'ABE3', 'ACAE', 'ACB1', 'ACB7', 'ACBA', 'AD2F', 'AD32', 'AE2B', 'AE2E', 'AE99', 'AEAA', 'AEBB', 'AEF5', 'AEF6', 'AEF8', 'AEFF', 'AF02', 'AF05', 'AF0B', 'AF0E', 'AF1A', 'AF8C', 'AFAB', 'B000', 'B001', 'B03E', 'B070', 'B0E9', 'B104', 'B107', 'B10A', 'B10D', 'B110', 'B137', 'B13D', 'B140', 'B149', 'B14C', 'B14F', 'B155', 'B158', 'B15B', 'B15E', 'B161', 'B164', 'B167', 'B16A', 'B16D', 'B1B9', 'B1BB', 'B1C3', 'B25E', 'B28C', 'B294', 'B29B', 'B29C', 'B29E', 'B2A0', 'B2A1', 'B2A6', 'B2C3', 'B2F2', 'B303', 'B3AA', 'B3AB', 'B3AC', 'B3B8', 'B3D2', 'B47D', 'B498', 'B499', 'B49A', 'B49B', 'B49C', 'B49D', 'B49E', 'B49F', 'B4C8', 'B4C9', 'B4CA', 'B4CC', 'B4CD', 'B4CF', 'B4D0', 'B503', 'B504', 'B505', 'B506', 'B50A', 'B50B', 'B5B8', 'B5BB', 'B5BE', 'B66D', 'B670', 'B671', 'B672', 'B673', 'B676', 'B677', 'B67A', 'B67B', 'B6A8', 'B6AB', 'B6AE', 'B700', 'B706', 'B71B', 'B71E', 'B721', 'B724', 'B727', 'B79A', 'B83D', 'B867', 'B86A', 'B90F', 'B915', 'B984', 'B9FE', 'BABA', 'BB57', 'BB59', 'BB5B', 'BB6A', 'BB6C', 'BBED', 'BBEF', 'BBF1', 'BC00', 'BC02', 'BC7B', 'BC7C', 'BCF2', 'BCF9', 'BD00', 'BD0E', 'BD13', 'BD1F', 'BD21', 'BD2B', 'BD34', 'BD58', 'BDE1', 'BEAA', 'BEE4', 'BFA4', 'BFD2', 'C063', 'C065', 'C067', 'C069', 'C06B', 'C06D', 'C06F', 'C071', 'C073', 'C075', 'C077', 'C079', 'C07B', 'C07D', 'C07F', 'C081', 'C083', 'C085', 'C087', 'C089', 'C08B', 'C08D', 'C08F', 'C091', 'C093', 'C095', 'C097', 'C099', 'C09B', 'C15E', 'C186', 'C1C1', 'C1EF', 'C270', 'C272', 'C274', 'C276', 'C278', 'C27A', 'C27C', 'C27E', 'C76F', 'C771', 'C773', 'C775', 'C777', 'C779', 'C77B', 'C77D', 'C77F', 'C7AA', 'C7AC', 'C7AE', 'C7B0', 'C7B2', 'C7B4', 'C7B6', 'C7B8', 'C7BA', 'C7BC', 'C7BE', 'C7C0', 'C7C2', 'C8C7', 'C8C9', 'C8CB', 'C8CD', 'C8CF', 'C8D1', 'C8D3', 'C8D5', 'C8D7', 'C8D9', 'C8DB', 'C8DD', 'C8E7', 'CF75', 'D247', 'D2DB', 'D2DE', 'D2E1', 'D2EA', 'D2ED', 'D2F0', 'D2F3', 'D2F6', 'D2FC', 'D2FF', 'D327', 'D362', 'D366', 'D36A', 'D3AB', 'D3AF', 'D4A2', 'D4A5', 'D4CC', 'D5FF', 'D689', 'D6EB', 'D7E8', 'D7FC', 'D810', 'D844', 'D8FA', 'D94F', 'D9A3', 'D9F7', 'DA51', 'DA88', 'DC0A', 'DC1A', 'DC36', 'DCA2', 'DCA7', 'DD03', 'DD1F', 'DE40', 'DEA7']

ffs = [int(s, 16) for s in ffs]

# make a test image of random data but with 0xFF's in the right places
data = bytearray()
for address in range(0xf000):
    x = 0xff
    if address in ffs:
        x = 0xFF
    else:
        x = 0x55
    data.append(x)

for address in range(0x02f0):
    if address not in ffs:
        data[address] = 0

for address in range(0xefe0, 0xf000):
    data[address] = 0xbf



# patch = {
#       0xa000: [0x00],               # start of nop slide
#       0xb29f: [0x13, 0x24, 0x00],   # mov pm4, #0
#       0xb3a9: [0x13, 0x25, 0x00],   # mov pm5, #0
#       0xb497: [0x0A, 0x05],         # set1 p5.0     loop
#       0xb499: [0x87,],              # mov a, [hl]
#       0xb49a: [0xF2, 0x04],         # mov p4, a
#       0xb49c: [0x0B, 0x05],         # clr1 p5.0
#       0xb49e: [0x86,],              # incw hl
#       0xb4c7: [0x9B, 0x97, 0xb4],   # br !loop
#       }
#
# # prefill patch area with NOPs to cover gaps between instructions
# start = min(patch.keys())
# end = max(patch.keys()) + len(patch[max(patch.keys())])
# for address in range(start, end):
#     data[address] = 0 # nop
#
# # write the patch
# for address_base, patch_bytes in patch.items():
#     for i, x in enumerate(patch_bytes):
#         address = address_base + i
#         data[address] = x
#
# # fill area after the patch with 0xFF
# for address in range(end, 0xf000):
#     data[address] = 0xff

with open('rom.bin', 'wb') as f:
    f.write(data)

os.system('srec_cat rom.bin -binary -o rom.hex -intel -address-length=2 -line-length=44 -crlf')
