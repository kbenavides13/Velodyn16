import json
import pprint
import sys
import dpkt
from velodyne import StatusState,process_frame,calc_coords


if len(sys.argv) < 3:
  print('usage: python {} <pcap_file> <out_file>'.format(sys.argv[0]))
  exit()

in_file = sys.argv[1]
out_file = sys.argv[2]


def firing_data_callback(laser_idx, rot_pos, dist, intensity):
  pass

status = StatusState()
print(status)
print('reading calibration from '+in_file)
with open(in_file, 'rb') as f:
  reader = dpkt.pcap.Reader(f)

  for ts, buf in reader:

    eth = dpkt.ethernet.Ethernet(buf)
    data = eth.data.data.data
    #print("status attributes pre:")
    #print(status.frame_idx)
    #print(status.block_idx)
    #print(status.laser_idx)
    #print(status.block_bytes)
    # 65 bytes, index starting at 1
    #print(status.raw_bytes)
    #print(status.values)
    #print(status.lasers[i].values for i in range(64))
    process_frame(data, 0, status, firing_data_callback)
    print(len(status.lasers[63].values))
    if len(status.lasers[63].values) > 0:
      break

lasers_cal = [status.lasers[l].values for l in range(64)]

#pprint.PrettyPrinter().pprint(lasers_cal)

print('writing calibration to '+out_file)
with open(out_file, 'w') as f:
  json.dump(lasers_cal, f, sort_keys=True, indent=4)
print('writing done')
