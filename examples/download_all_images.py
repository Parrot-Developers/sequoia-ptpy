#!/usr/bin/env python
import ptpy

camera = ptpy.PTPy()

with camera.session():
    handles = camera.get_object_handles(
        0,
        all_storage_ids=True,
        all_formats=True,
    )
    for handle in handles:
        info = camera.get_object_info(handle)
        print(info)
        # Download all things that are not groups of other things.
        if info.ObjectFormat != 'Association':
            obj = camera.get_object(handle)
            with open(info.Filename, mode='w') as f:
                f.write(obj.Data)
