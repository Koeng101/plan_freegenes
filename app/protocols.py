import requests 
import json
import uuid

def glycerol_to_deepwell(full_plate):
    def derive_plate(plate, protocol_uuid, new_plate_uuid):
        return {
      "breadcrumb": "",
      "plate_form": "deep96",
      "plate_name": "{}_culture".format(full_plate['plate_name']),
      "plate_type": "deepwell_culture",
      "protocol_uuid": protocol_uuid,
      "status": "Culturing",
      "uuid": new_plate_uuid
    }

    def human_protocol_deepwell(glycerol_plate, protocol_uuid, new_plate_uuid):
        return {'protocol': {'human_protocol': ['Prepare a deepwell plate labeled {} with 1.2mL of broth'.format(new_plate_uuid),
                                 'Pin {}'.format(glycerol_plate['uuid']),
                                 'Transfer to {}'.format(new_plate_uuid),
                                 'Ethanol rinse and flame pins',
                                 'Reseal and refreeze {}'.format(glycerol_plate['uuid'])]},
                    'description': 'Human protocol to pin glycerol stocks and tranfer to deepwell plates',
                    'status': None,
                    'protocol_type': 'human_v1',
                    'uuid': protocol_uuid
                   }

    def derive_sample(sample):
        return {
            'derived_from': sample['uuid'],
            'evidence': 'Derived_From_{}'.format(sample['evidence']),
            'part_uuid': sample['part_uuid'],
            'status': sample['status'],
            'uuid': str(uuid.uuid4())
        }
    def derive_well(well,new_sample,plate_uuid,volume=1200,media='lb',well_type='culture'):
        return {
          "address": well['address'],
          "media": media,
          "organism": well['organism'],
          "plate_uuid": plate_uuid,
          "volume": volume,
          "well_type": well_type,
            'samples': [new_sample['uuid']]
        }

    new_plate_uuid = str(uuid.uuid4())
    protocol_uuid = str(uuid.uuid4())

    plate = derive_plate(full_plate, protocol_uuid, new_plate_uuid)
    protocol = human_protocol_deepwell(full_plate, protocol_uuid, new_plate_uuid)

    old_wells = [well for well in full_plate['wells']]

    new_wells = []
    new_samples = []
    new_well = None
    new_sample = None

    for well in old_wells:
        for sample in well['samples']:
            new_sample = derive_sample(sample)
            new_samples.append(new_sample)
        new_well = derive_well(well,new_sample,new_plate_uuid)
        new_wells.append(new_well)

    updates = {'protocols': {'post': [protocol]},
           'plates': {'post': [plate]},
           'samples': {'post': [new_samples]},
           'wells': {'post': [new_wells]},}
    return updates


