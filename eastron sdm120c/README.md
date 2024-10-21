Do not read out concurrently, as they are daisy chained to a single RS485 converter. Instead read them sequentially using a cron entry like this:

*/1 * * * * /opt/scripts/sdm120c_ecolution.sh >/dev/null 2>&1; /opt/scripts/sdm120c_aquarea.sh >/dev/null 2>&1; /opt/scripts/sdm120c_aquarea_heater.sh >/dev/null 2>&1

