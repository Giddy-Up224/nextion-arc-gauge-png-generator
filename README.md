# arc-gauge-png-generator

* Generate PNG files to use in Nextion style displays

## How to use

* Simply run `src/main.py`, it will output the png files to the `out` folder.
* You can change the colors and sizes etc. in the `src/main.py` file
* If you're rerunning the creation, you can delete the old png files in `out` via the `delete-pngs` task
* The start/stop points are a bit weird because of the `PIL` library used for creating the images. You gotta fiddle around to get it right.

```python
#################################################################
##################      USER SETTINGS          ##################
#################################################################
DISPLAY_SIZE     = 200
MARGIN           = 20
SCALE            = 4
ARC_THICKNESS    = 15
ARC_START_ANGLE  = 270
ARC_STOP_ANGLE   = 90
ARC_COLOR        = (0, 0, 255) # Red, Green, Blue
ARC_BG_COLOR     = (0, 100, 100) # Red, Green, Blue
TICK_STEP        = 2 # Step size. Example: 5 will produce 20 pngs, 2 will produce 50 pngs
```


<img src="img/cmd_palette.png">
<img src="img/delete_pngs_task.png">

## Credits

- Give credit where credit is due...