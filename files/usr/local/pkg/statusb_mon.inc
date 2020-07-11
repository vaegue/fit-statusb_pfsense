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
//	TODO: potential arguments to script
	write_rcfile(array(
		'file' => 'statusb_mon.sh',
		'start' => '/usr/local/bin/statusb_mon.py &',
		'stop' => 'kill -2 `cat /var/run/statusb_mon.pid`')
	);
}

function sync_package_statusb_mon() {
	global $config;

	statusb_mon_rcfile();

	$statusb_mon_config = $config['installedpackages']['statusb_mon']['config'][0];
	/* If the service (being) disabled, stop it (if running) and do nothing else */
	if (!($statusb_mon_config['enable'])) {
		if (is_process_running("statusb_mon.py")) {
			stop_service("statusb_mon");
		}
		return;
	}
	/* Kill all instances of statusb_mon */
	if (is_process_running("statusb_mon.py")) {
		stop_service("statusb_mon");
	}
	start_service("statusb_mon");
}

?>
