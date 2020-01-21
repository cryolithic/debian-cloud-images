# SPDX-License-Identifier: GPL-2.0-or-later

import pytest
import subprocess
import tarfile

from unittest.mock import Mock

from debian_cloud_images.build.tar import RunTar


class TestRunTar:
    def test___call__(self, tmp_path):
        input_filename = tmp_path / 'in'
        output_filename = tmp_path / 'out'
        run = RunTar(
            input_filename=input_filename,
            output_filename=output_filename,
            inner_filename='file',
        )
        popen_proc = Mock()
        popen_proc.wait = Mock(return_value=0)
        popen = Mock(return_value=popen_proc)

        run(True, popen=popen)

        popen.assert_called_with(
            (
                'tar',
                '--create',
                '--absolute-names',
                '--file', output_filename.as_posix(),
                '--sparse',
                '--transform', r's/.*/file/',
                input_filename.as_posix(),
            ),
        )
        popen_proc.wait.assert_called()

    def test___call___fail(self, tmp_path):
        input_filename = tmp_path / 'in'
        output_filename = tmp_path / 'out'
        run = RunTar(
            input_filename=input_filename,
            output_filename=output_filename,
            inner_filename='file',
        )
        popen_proc = Mock()
        popen_proc.wait = Mock(return_value=23)
        popen = Mock(return_value=popen_proc)

        with pytest.raises(subprocess.CalledProcessError) as excinfo:
            run(True, popen=popen)

        assert excinfo.value.returncode == 23

    def test___call___noop(self, tmp_path):
        input_filename = tmp_path / 'in'
        output_filename = tmp_path / 'out'
        run = RunTar(
            input_filename=input_filename,
            output_filename=output_filename,
            inner_filename='file',
        )
        popen = Mock()

        run(False, popen=popen)

        popen.assert_not_called()

    def test___call___real(self, tmp_path, capfd):
        input_filename = tmp_path / 'in'
        output_filename = tmp_path / 'out'
        run = RunTar(
            input_filename=input_filename,
            output_filename=output_filename,
            inner_filename='file',
        )

        with input_filename.open('w') as f:
            f.write('content')

        run(True)

        with output_filename.open('rb') as f:
            with tarfile.TarFile(fileobj=f) as t:
                members = t.getmembers()
                assert len(members) == 1
                assert members[0].name == 'file'

        captured = capfd.readouterr()
        assert not captured.out
        assert not captured.err
