# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from twisted.trial import unittest
from buildbot.steps.source import darcs
from buildbot.status.results import SUCCESS
from buildbot.test.util import sourcesteps
from buildbot.test.fake.remotecommand import ExpectRemoteRef, ExpectShell, Expect
from buildbot.steps.transfer import _FileReader
from buildbot import config

class TestDarcs(sourcesteps.SourceStepMixin, unittest.TestCase):

    def setUp(self):
        return self.setUpSourceStep()

    def tearDown(self):
        return self.tearDownSourceStep()

    def test_no_empty_step_config(self):
        self.assertRaises(config.ConfigErrors, lambda: darcs.Darcs())

    def test_incorrect_method(self):
        self.assertRaises(config.ConfigErrors, lambda:
                              darcs.Darcs(repourl='http://localhost/darcs',
                                          mode='full', method='fresh'))

    def test_incremental_invalid_method(self):
        self.assertRaises(config.ConfigErrors, lambda:
                              darcs.Darcs(repourl='http://localhost/darcs',
                                          mode='incremental', method='fresh'))

    def test_no_repo_url(self):
        self.assertRaises(config.ConfigErrors, lambda:
                              darcs.Darcs(mode='full', method='fresh'))

    def test_mode_full_clobber(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='full', method='clobber'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True))
            + 0,
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()


    def test_mode_full_copy(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='full', method='copy'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True,
                                 timeout=1200))
            + 0,
            Expect('stat', dict(file='source/_darcs',
                                logEnviron=True))
            + 0,
            ExpectShell(workdir='source',
                        command=['darcs', 'pull', '--all', '--verbose'])
            + 0,
            Expect('cpdir', {'fromdir': 'source', 'todir': 'build',
                             'logEnviron': True, 'timeout': 1200})
            + 0,
            ExpectShell(workdir='build',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_no_method(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='full'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True,
                                 timeout=1200))
            + 0,
            Expect('stat', dict(file='source/_darcs',
                                logEnviron=True))
            + 0,
            ExpectShell(workdir='source',
                        command=['darcs', 'pull', '--all', '--verbose'])
            + 0,
            Expect('cpdir', {'fromdir': 'source', 'todir': 'build',
                             'logEnviron': True, 'timeout': 1200})
            + 0,
            ExpectShell(workdir='build',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='incremental'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('stat', dict(file='wkdir/_darcs',
                                logEnviron=True))
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'pull', '--all', '--verbose'])
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental_patched(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='incremental'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 0,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True,
                                 timeout=1200))
            + 0,
            Expect('stat', dict(file='source/_darcs',
                                logEnviron=True))
            + 0,
            ExpectShell(workdir='source',
                        command=['darcs', 'pull', '--all', '--verbose'])
            + 0,
            Expect('cpdir', {'fromdir': 'source', 'todir': 'build',
                             'logEnviron': True, 'timeout': 1200})
            + 0,

            Expect('stat', dict(file='build/_darcs',
                                logEnviron=True))
            + 0,
            ExpectShell(workdir='build',
                        command=['darcs', 'pull', '--all', '--verbose'])
            + 0,
            ExpectShell(workdir='build',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental_patch(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='incremental'),
                patch=(1, 'patch'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('stat', dict(file='wkdir/_darcs',
                                logEnviron=True))
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'pull', '--all', '--verbose'])
            + 0,
            Expect('downloadFile', dict(blocksize=16384, maxsize=None, 
                                        reader=ExpectRemoteRef(_FileReader),
                                        slavedest='.buildbot-diff', workdir='wkdir',
                                        mode=None))
            + 0,
            Expect('downloadFile', dict(blocksize=16384, maxsize=None, 
                                        reader=ExpectRemoteRef(_FileReader),
                                        slavedest='.buildbot-patched', workdir='wkdir',
                                        mode=None))
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['patch', '-p1', '--remove-empty-files',
                                 '--force', '--forward', '-i', '.buildbot-diff'])
            + 0,
            Expect('rmdir', dict(dir='wkdir/.buildbot-diff',
                                 logEnviron=True))
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()


    def test_mode_full_clobber_retry(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='full', method='clobber', retry=(0, 2)))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True))
            + 0,
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True))
            + 0,
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True))
            + 0,
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_full_clobber_revision(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='full', method='clobber'),
                            dict(revision='abcdef01'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('rmdir', dict(dir='wkdir',
                                 logEnviron=True))
            + 0,
            Expect('downloadFile', dict(blocksize=16384, maxsize=None, 
                                        reader=ExpectRemoteRef(_FileReader),
                                        slavedest='.darcs-context', workdir='wkdir',
                                        mode=None))
            + 0,
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', '--context',
                                 '.darcs-context', 'http://localhost/darcs'])
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

    def test_mode_incremental_no_existing_repo(self):
        self.setupStep(
                darcs.Darcs(repourl='http://localhost/darcs',
                                    mode='incremental'))
        self.expectCommands(
            ExpectShell(workdir='wkdir',
                        command=['darcs', '--version'])
            + 0,
            Expect('stat', dict(file='wkdir/.buildbot-patched',
                                logEnviron=True))
            + 1,
            Expect('stat', dict(file='wkdir/_darcs',
                                logEnviron=True))
            + 1,
            ExpectShell(workdir='.',
                        command=['darcs', 'get', '--verbose', '--lazy',
                                 '--repo-name', 'wkdir', 'http://localhost/darcs'])
            + 0,
            ExpectShell(workdir='wkdir',
                        command=['darcs', 'changes', '--max-count=1'])
            + ExpectShell.log('stdio',
                              stdout='Tue Aug 20 09:18:41 IST 2013 abc@gmail.com')
            + 0,
        )
        self.expectOutcome(result=SUCCESS, status_text=["update"])
        self.expectProperty('got_revision', 'Tue Aug 20 09:18:41 IST 2013 abc@gmail.com', 'Darcs')
        return self.runStep()

