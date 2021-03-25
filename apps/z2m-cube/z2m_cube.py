import appdaemon.plugins.hass.hassapi as hass
import globals
import json

class Z2Mcube(hass.Hass):
    def initialize(self):
        self.listen_state_handle_list = []

        self.cube = globals.get_arg(self.args, "cube")
        self.actions = globals.get_arg(self.args, "actions")

        self.action_dict = json.loads(str(self.actions))
        self.listen_state_handle_list.append(
            self.listen_state(self.state_change, self.cube)
        )

    def state_change(self, entity, attribute, old, new, kwargs):
        if new != "":
            self.log("{} changed from {} to {}".format(entity, old, new))
            panel = self.get_state(entity, attribute="side")
            rotation = self.get_state(entity, attribute="angle")
            if new == "tap":
                self.tap(panel)
            elif new == "rotate_left":
                self.rotate_left(panel, rotation)
            elif new == "rotate_right":
                self.rotate_right(panel, rotation)
        
    def rotate_right(self, panel, rotation):
        self.log("triggering rotate_right action")
        try: 
            site = self.get_site("rotate_right", panel)
            self.rotate(site, rotation)
        except: 
            self.log("cant execute rotate_left for "+str(panel)+"")
    
    def rotate_left(self, panel, rotation):
        self.log("triggering rotate_left action")
        try:
            site = self.get_site("rotate_left", panel)
            self.rotate(site, rotation)
        except: 
            self.log("cant execute rotate_left for "+str(panel)+"")


    def tap(self, panel):
        self.log("triggering tap action")
        try: 
            site = self.get_site("tap", panel)
            self.call_service(
                str(site['service'].replace(".","/")), entity_id=str(site['entity'])
            )
            self.log("executed: "+str(site))
        except:
            self.log("cant execute tap for "+str(panel)+"")

    
    def rotate(self, site, rotation):
        device = site["entity"]
        device = device[0:device.index(".")]
        if device == "light":                
            value = self.get_state(str(site['entity']), attribute="brightness")
            if str(value) == "None":
                value = 0
            rotation = round(rotation)
            value = value + rotation
            if value >= 255:
                value = 255
            elif value <= 0:
                value = 0
            self.call_service(
                str(site['service'].replace(".","/")), entity_id=str(site['entity']), brightness=str(value), transition=1
            )

    def strip_array(self, array):
        array = array[1:len(array)-1]
        array = array.replace("'","\"")
        array = json.loads(str(array))
        return array
    
    def get_site(self, action, panel):
        sites = self.strip_array(str(self.action_dict[str(action)]))
        site = self.strip_array(str(sites[str(panel)]))
        return site