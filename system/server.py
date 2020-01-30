# Standard Libs
import json
import os
import subprocess
import configparser
# Installed Libs
import cherrypy


# Todo: too many config_parse blocks, create a function to easily call it

class SDCardDupe(object):
    @cherrypy.expose
    def index(self):
        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )


        # Get webpage, then replace needed parts here
        www_path = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1]) + "/www/"
        html_string = open(www_path + 'index.html', 'r').read()
        hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        html_string = html_string.replace("replacewithhostnamehere",'/')

        css_string = '<style>' + open(config_parse['DuplicatorSettings']['SkeletonLocation'], 'r').read() + '</style>'
        html_string = html_string.replace("<style></style>",css_string)
        html_string = html_string.replace("$IMG_ROOT$", config_parse['DuplicatorSettings']['ImagePath'])
        if 'BalenaAppId' in config_parse['DuplicatorSettings']:
            balena_app_id = config_parse['DuplicatorSettings']['BalenaAppId']
        else:
            balena_app_id = "false"

        html_string = html_string.replace("$BALENA_APP_ID$", balena_app_id)
        return html_string


    @cherrypy.expose
    def monitor(self):

        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        # Get webpage, then replace needed parts here
        www_path = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1]) + "/www/"
        html_string = open(www_path + 'monitor.html', 'r').read()
        hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        html_string = html_string.replace("replacewithhostnamehere",'/')

        css_string = '<style>' + open(config_parse['DuplicatorSettings']['SkeletonLocation'], 'r').read() + '</style>'
        html_string = html_string.replace("<style></style>",css_string)

        return html_string

    @cherrypy.expose
    def posted(self,img_file,devices):

        # get all mounted items on the rpi
        mounted_list = []
        mounted_volumes_output = subprocess.check_output("mount", shell=True)
        for mount_line in str(mounted_volumes_output.decode("utf-8")).split("\n"):
            device_name = mount_line.split(" on ",1)[0]
            if device_name not in mounted_list:
                mounted_list.append(device_name)

        # If one device has been posted, a string is passed into function
        # Need to convert to a list
        if type(devices) is str:
            devices = [devices]

        # nested for loop, maybe we can optimize this later
        for dev_path in devices:

            reduced_list = []
            for mounted_item in mounted_list:
                # assumptions made, there will be no collisions, dont have to pop element
                # but to reduce the cost of loop, will pop element by creating new list
                if dev_path in mounted_item:
                    umount_disk_cmd = "umount %s"%mounted_item
                    subprocess.call(umount_disk_cmd.split(" "))
                else:
                    reduced_list.append(mounted_item)

            mounted_list = []
            mounted_list.extend(reduced_list)


        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        if not os.path.exists(config_parse['DuplicatorSettings']['Logs']):
            os.makedirs(config_parse['DuplicatorSettings']['Logs'])

        #Save current img name to logs
        with open(config_parse['DuplicatorSettings']['Logs'] + "/imagename.info", 'w') as out:
            out.write(os.path.basename(img_file))
        out.close()

        # Run dd command and output status into the progress.info file
        dd_cmd = "dcfldd bs=4M if=" + img_file
        dd_cmd += " of=" + " of=".join(devices)
        dd_cmd += " sizeprobe=if statusinterval=1 2>&1 | tee "
        dd_cmd += config_parse['DuplicatorSettings']['Logs'] + "/progress.info"
        dd_cmd += " && echo \"osid_completed_task\" | tee -a "
        dd_cmd += config_parse['DuplicatorSettings']['Logs'] + "/progress.info"

        # Planned to run this in localhost only.
        # But if there are plans to put this on the network, this is a security issue
        # Just a workaround to get it running by subprocess
        dd_cmd_file = config_parse['DuplicatorSettings']['Logs']+"/run.sh"
        with open(dd_cmd_file,'w') as write_file:
            write_file.write(dd_cmd)

        subprocess.Popen(['sudo', 'bash', dd_cmd_file], close_fds=True)

        hostname_port = config_parse['DuplicatorSettings']['Host']+":"+config_parse['DuplicatorSettings']['SocketPort']
        monitor_url = "/monitor";


        html_string = "<html><head>"
        html_string += "<meta http-equiv=\"refresh\" content=\"0; URL='" +monitor_url+ "'\" />"
        html_string += "</head></html>"

        return html_string



    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getStatus(self):
        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )
        progress_file = config_parse['DuplicatorSettings']['Logs'] + "/progress.info"

        # pull data from imagename.info for image name
        with open(config_parse['DuplicatorSettings']['Logs'] + "/imagename.info", 'r') as out:
            imgname = out.read()
        out.close()

        # pull data from progress.info file and feed back to call
        cat_cmd = "cat "+ progress_file
        cat_output = str(subprocess.check_output(cat_cmd, shell=True).decode("utf-8"))
        if "records in" in cat_output and "records out" in cat_output and "osid_completed_task" in cat_output:
            percentage = "100%"
            time_remains = "00:00:00"

        elif "%" in cat_output:
            current_line = cat_output.split("[")[-1]
            percentage = current_line.split(" of ")[0]
            time_remains = current_line.split("written. ")[1].split(" remaining.")[0]

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps({'percentage':percentage.replace('%',''),'time_remaining':time_remains,'img_name':imgname})


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getDevices(self):

        list_devices = []

        # Refresh partition to discover all available medias
        refresh_disk_cmd = "/sbin/partprobe"
        subprocess.check_output(refresh_disk_cmd, shell=True)

        # command to get a list of devices on OS
        get_disk_cmd = "lsblk -d | awk -F: '{print $1}' | awk '{print $1}'"
        cmd_device_list_output = subprocess.check_output(get_disk_cmd, shell=True)

        # break down the list to only usb devices
        for device_name in str(cmd_device_list_output.decode("utf-8")).split("\n"):
            if len(device_name) > 0 and 'NAME' not in device_name and 'mmcblk0' not in device_name:

                # get the block size of the device and the gb size
                get_disksize_cmd = "cat /sys/block/" + device_name + "/size"
                cmd_blocksize_output = subprocess.check_output(get_disksize_cmd, shell=True).decode("utf-8").rstrip("\n")
                device_size_gb = str(round(((int(cmd_blocksize_output) / 2) / 1024) / 1024, 2)) + 'G';
                # list_devices[device_name] = str(device_size_gb) + 'G'
                list_devices.append({'name': "/dev/"+device_name, 'size': device_size_gb})

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        # return json.dumps(dict(Devices=list_devices))
        return json.dumps(list_devices)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getImages(self):

        list_images = []

        # get the path of images from the ini file
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

        # get the list of images and check if valid img file
        for img_file in os.listdir(config_parse['DuplicatorSettings']['ImagePath']):
            img_fullpath = os.path.join(config_parse['DuplicatorSettings']['ImagePath'], img_file)
            if os.path.isfile(img_fullpath) and  os.path.splitext(img_file)[1] == '.img':

                # get the size of the image
                img_filesize_cmd = "ls -sh " + img_fullpath
                img_size_cmd_output = subprocess.check_output(img_filesize_cmd, shell=True).decode("utf-8").rstrip("\n")

                # output is "Size Filename"
                # img_size_gb = round(((int(img_size_cmd_output.split(' ')[0]) / 2) / 1024) / 1024, 2);
                img_size_gb = img_size_cmd_output.split(' ')[0]

                # prep the data to send
                list_images.append({'filename': img_file, 'fullpath': img_fullpath, 'filesize': img_size_gb})

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(list_images)



if __name__ == '__main__':

    # get host configs from server.ini
    # note: is there a way to put the config into conf and pull from api functions
    config_parse = configparser.ConfigParser()
    config_parse.sections()
    config_parse.read( os.path.dirname(os.path.realpath(__file__)) + '/server.ini' )

    conf = {
        'global':{
            'server.socket_host': config_parse['DuplicatorSettings']['Host'],
            'server.socket_port': int(config_parse['DuplicatorSettings']['SocketPort']),
            'log.access_file' : config_parse['DuplicatorSettings']['Logs']+"/access.log",
            'log.screen': False,
            'tools.sessions.on': True
        },
        '/favicon.ico':{
            'tools.staticfile.on': True,
            'tools.staticfile.filename': "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1]) + "/www/favicon.ico"
        }
    }

    # create a daemon for cherrpy so it will create a thread when started
    #cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()

    cherrypy.quickstart(SDCardDupe(), '/', conf)
