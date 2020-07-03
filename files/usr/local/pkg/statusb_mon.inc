<?php
/*
 * statusb_mon.inc
 *
 * part of pfSense (https://www.pfsense.org)
 * Copyright (c) 2009-2020 Rubicon Communications, LLC (Netgate)
 * All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
require_once("config.inc");
require_once("functions.inc");

function statusb_mon_rcfile() {
	global $config;
	$statusb_mon_config = $config['installedpackages']['statusb_mon']['config'][0];
	$stop = <<<EOD
if [ `/bin/pgrep statusb_mon | /usr/bin/wc -l` != 0 ]; then
		/usr/bin/killall -9 statusb_mon
		while [ `/bin/pgrep statusb_mon | /usr/bin/wc -l` != 0 ]; do
			sleep 1
		done
	fi
EOD;

	$start = "{$stop}\n";
	if (($statusb_mon_config['enable_led2']) && ($statusb_mon_config['iface_led2']))
		$start .= "\t" . statusb_mon_launch(convert_friendly_interface_to_real_interface_name($statusb_mon_config['iface_led2']), 2, true) . "\n";
	if (($statusb_mon_config['enable_led3']) && ($statusb_mon_config['iface_led3']))
		$start .= "\t" . statusb_mon_launch(convert_friendly_interface_to_real_interface_name($statusb_mon_config['iface_led3']), 3, true) . "\n";

	write_rcfile(array(
		'file' => 'statusb_mon.sh',
		'start' => $start,
		'stop' => $stop)
	);
}

function sync_package_statusb_mon() {
	global $config;

	statusb_mon_rcfile();

	$statusb_mon_config = $config['installedpackages']['statusb_mon']['config'][0];
	/* If the service (being) disabled, stop it (if running) and do nothing else */
	if (!($statusb_mon_config['enable'])) {
		if (is_process_running("statusb_mon")) {
			stop_service("statusb_mon");
		}
		return;
	}
	/* Kill all instances of statusb_mon */
	if (is_process_running("statusb_mon")) {
		stop_service("statusb_mon");
	}
	start_service("statusb_mon");
}

function statusb_mon_launch($int, $led, $return = false) {
	$cmd = "/usr/local/bin/statusb_mon -i " . escapeshellarg($int) . " -l " . escapeshellarg("/dev/led/led{$led}");
	if ($return) {
		return $cmd;
	} else {
		mwexec($cmd);
	}
}

function validate_form_statusb_mon($post, &$input_errors) {
	/* Make sure both aren't using the same interface */
	if (($post['iface_led2']) && ($post['iface_led3']) &&
	    (($post['enable_led2']) && ($post['enable_led3'])) &&
	    ($post['iface_led2'] == $post['iface_led3'])) {
		$input_errors[] = 'You cannot set two LEDs for a single interface. Please choose seperate interfaces.';
	}
}

?>
