# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
import psutil

__all__ = ['CheckPlan']
__metaclass__ = PoolMeta


def check_output(*args):
    import subprocess
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    process.wait()
    data = process.stdout.read()
    return data


class CheckPlan:
    __name__ = 'monitoring.check.plan'

    def check_backup(self):
        path = self.item.get_attribute('backup_paths')
        output = check_output('rdiff-backup', '--list-increment-size', path)
        lines = [x for x in output.splitlines() if '(current mirror)' in x]
        if not lines:
            return [{
                'result': 'backup',
                'char_value': res,
                }]
        res = 'OK'
        res = [{
            'result': 'backup',
            'char_value': 'OK',
            }]
        date, size, size_unit, cum_size, cum_size_unit = lines[0].split(' ')[:5]
        res.append({
                'result': 'backup_size',
                'float_value': size,
                })
        res.append({
                'result': 'backup_cumulative_size',
                'float_value': cum_size,
                })
        return res
