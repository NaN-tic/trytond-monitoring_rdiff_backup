# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import subprocess
import json
from datetime import datetime
from trytond.pool import PoolMeta

__all__ = ['CheckPlan']
__metaclass__ = PoolMeta


def check_output(*args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    process.wait()
    data = process.stdout.read()
    stderr = process.stderr.read()
    return data, stderr


def to_bytes(value, unit):
    if 'unit' == 'TB':
        return value * 1000 * 1000 * 1000 * 1000
    if 'unit' == 'GB':
        return value * 1000 * 1000 * 1000
    if 'unit' == 'MB':
        return value * 1000 * 1000
    if 'unit' == 'KB':
        return value * 1000
    return value


def fields(line):
    line = line.split()
    date = ' '.join(line[:5])
    return {
        'date': datetime.strptime(date, '%a %b %d %H:%M:%S %Y'),
        'size': line[5],
        'size_unit': line[6],
        'cum_size': line[7],
        'cum_size_unit': line[8],
        }


class CheckPlan:
    __name__ = 'monitoring.check.plan'

    def check_rdiff_backup(self):
        path = self.get_attribute('backup_path')
        output, stderr = check_output('rdiff-backup', '--list-increment-size', path)
        lines = output.splitlines()
        current = [x for x in lines if '(current mirror)' in x]
        if not current:
            return [{
                'result': 'rdiff_backup_status',
                'char_value': 'Error',
                'payload': json.dumps({
                            'output': stderr,
                            })
                }]
        res = 'OK'
        res = [{
            'result': 'rdiff_backup_status',
            'char_value': 'OK',
            }]
        first = fields(current[0])
        last = fields(lines[-1])
        elapsed_hours = (datetime.now() - first['date']).total_seconds() / 3600

        res.append({
                'result': 'rdiff_backup_size',
                'float_value': to_bytes(first['size'], first['size_unit']),
                })
        res.append({
                'result': 'rdiff_backup_cumulative_size',
                'float_value': to_bytes(last['cum_size'], last['cum_size_unit'])
                })
        res.append({
                'result': 'rdiff_backup_age',
                'float_value': elapsed_hours,
                })
        return res
