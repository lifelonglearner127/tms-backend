
def get_branches(job):
    branches = []
    for job_station in job.jobstation_set.all()[2:]:
        for job_station_product in job_station.jobstationproduct_set.all():
            order_product = job.order.orderproduct_set.filter(product=job_station_product.product).first()
            for branch in branches:
                if branch['branch'] == job_station_product.branch:
                    branch['unloading_stations'].append({
                        'unloading_station': {
                            'address': job_station.station.address,
                            'time': job_station_product.due_time.strftime("%Y-%m-%d %H:%M")
                        },
                        'weight': str(job_station_product.mission_weight)
                        + order_product.get_weight_measure_unit_display()
                    })
                    break
            else:
                branches.append({
                    'branch': job_station_product.branch,
                    'product': job_station_product.product.name,
                    'unloading_stations': [{
                        'unloading_station': {
                            'address': job_station.station.address,
                            'time': job_station_product.due_time.strftime("%Y-%m-%d %H:%M")
                        },
                        'weight': str(job_station_product.mission_weight)
                        + order_product.get_weight_measure_unit_display()
                    }]
                })

    return branches
