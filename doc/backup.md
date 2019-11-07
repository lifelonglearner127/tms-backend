## Automated Database backup
You can see the db backup script `backups` directory. You need to edit some configuration based on your server setting.
Automated backup should be run as a cron job so you need to configure cronjob as well.

 - Settings that need to be changed in `pg_backup.sh` file
    - BACKUP_DIR: the path into which backup files will created
    - DATABASE: database name you need to backup
    - USER: database user
    - make this file executable
        ```
        chmod +x pg_backup.sh
        ```

 - How to create a cron job
    ```
    crontab -e
    0 0 * * * /root/Projects/tms-backend/backups/pg_backup.sh
    ```
    > this cronjob will run the script every day at 0.0 a.m

 - Remember creating `.pgpass` in your home directory, take a look at [here](https://www.postgresql.org/docs/9.3/libpq-pgpass.html)
 - Restore the database from backup
   ```
   psql -U dev -d tms -f db.sql
   ```
