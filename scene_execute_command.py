import obspython as obs
import subprocess
import shlex
settings = {}

def script_description():
  return '''<h2>Execute a CLI command when scene is activated.</h2>
              <p>Original script by <a href="https://github.com/marklagendijk">Mark Lagendijk
</a>. Rewritten in Python by <a href="https://github.com/JosephSamela">Joe Samela</a>.
            <h3>Instructions:</h3>
            <p>In the form below enter the command you want to execute with text <code>SCENE_VALUE</code> in-place of the command argument. For each scene, specify the value you want to pass into the command. When activating a scene the command will execute with the text <code>SCENE_VALUE</code> replaced with the value for that scene.</p>
            <h3>Example:</h3>
            <p>For command:</p>
            <p><code>curl -X POST http://192.168.1.123/load-preset -d "preset=SCENE_VALUE"</code></p>
            <p>And Scene 1 value is <code>5</code>.</p>
            <p>Activating Scene 1 would execute:</p>
            <p><code>curl -X POST http://192.168.1.123/load-preset -d "preset=5"</code></p>'''

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "command", "Command", obs.OBS_TEXT_DEFAULT)
    scenes = obs.obs_frontend_get_scenes()
    if scenes != None:
        for scene in scenes:
            scene_name = obs.obs_source_get_name(scene)
            obs.obs_properties_add_bool(props, f"scene_enabled_{scene_name}", f"Execute when {scene_name} is activated")
            obs.obs_properties_add_text(props, f"scene_value_{scene_name}", f"{scene_name} value", obs.OBS_TEXT_DEFAULT)
    obs.source_list_release(scenes)
    return props

def script_update(_settings):
    global settings
    settings = _settings

def script_load(settings):
    obs.obs_frontend_add_event_callback(handle_event)

def handle_event(event):
    if event == obs.OBS_FRONTEND_EVENT_SCENE_CHANGED:
        handle_scene_change()

def handle_scene_change():
    scene = obs.obs_frontend_get_current_scene()
    scene_name = obs.obs_source_get_name(scene)
    scene_enabled = obs.obs_data_get_bool(settings, f"scene_enabled_{scene_name}")
    if scene_enabled:
        command = obs.obs_data_get_string(settings, "command")
        scene_value = obs.obs_data_get_string(settings, f"scene_value_{scene_name}")
        scene_command = shlex.split(command.replace("SCENE_VALUE", scene_value))
        print(f"Activating {scene_name}. Executing command: {scene_command}")
        result = subprocess.run(scene_command, shell=True)
        print(result)
    else:
        print(f"Activating {scene_name}. Command execution is disabled for this scene.")
    
    obs.obs_source_release(scene)
