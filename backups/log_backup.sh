BACKUP_DIR=/root/backups
DAYS_TO_KEEP=14
FILE="tms_asgimqtt_`"%Y-%m-%d_%H:%M"`.log"

OUTPUT_FILE=${BACKUP_DIR}/${FILE}

mv tms_asgimqtt.log $OUTPUT_FILE
# gzip the mysql database dump file
gzip $OUTPUT_FILE

# show the user the result
echo "${OUTPUT_FILE}.gz was created:"
ls -l ${OUTPUT_FILE}.gz

# prune old backups
find $BACKUP_DIR -maxdepth 1 -mtime +$DAYS_TO_KEEP -name "*${FILE_SUFFIX}.gz" -exec rm -rf '{}' ';'
