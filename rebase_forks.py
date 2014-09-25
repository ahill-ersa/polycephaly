#!/usr/bin/env python3

"""
Graphical interface for rebasing all git forks

Requires: python-tk
"""
from tkinter import *
from tkinter import ttk
import re
import os
from subprocess import *
import argparse
import configparser

class ForkRebase(Exception):
    """
    Raised for errors in this script
    """

class RepoFork(object):
    """
    Represents a repository fork
    """

    def __init__(self, basedir, dirname):
        """
        Initialize a repo fork

        basedir is an absolute path
        dirname is a path relative to basedir
        """
        # Set up the base path variables
        # NOTE: This assumes that the paths have been checked elsewhere.
        self.basedir = basedir
        self.dirname = "%s/%s" % (self.basedir, dirname)

        # cd into our fork directory
        os.chdir(self.dirname)

        # Get the remotes for the current
        self.remotes = None
        self.get_remotes()

        # Get the current branch
        self.current_branch = None
        self.get_current_branch()

    def get_remotes(self):
        """
        Work out the remote repositories for this fork
        """

        if not self.remotes:
            self.remotes = {}

            # Run git and parse out the remotes that we are pushing to.
            remotes_re = re.compile(
                r'\s*(?P<name>.*?)'\
                r'\s+(?P<url>.*?)'\
                r'\s+.*push.*$'
            )

            try:
                # Run the git remote command
                remote_command = Popen(
                    ['git', 'remote', '-v'],
                    stdout=PIPE,
                    stderr=PIPE
                )
                (stdout, stderr) = remote_command.communicate()[:2]

                if remote_command.returncode != 0:
                    raise ForkRebase(
                        'Failed to run \'git remote\'.\n%s' % stderr
                    )

                # Parse out all of the push type branches.
                for line in stdout.decode('utf-8').split('\n'):
                    matches = remotes_re.search(line)
                    if matches:
                        self.remotes[matches.group('name')] =\
                            matches.group('url')

            except CalledProcessError:
                raise ForkRebase('Could not find any remote repo definitions.')

        return self.remotes

    def get_current_branch(self):
        """
        Get the current branch
        """

        if not self.current_branch:
            # Run git status and get the current branch
            branches_re = re.compile(
                r'\*\s+(?P<name>.*)$'\
            )

            try:
                # Run the git branch command
                branch_command = Popen(
                    ['git', 'branch'],
                    stdout=PIPE,
                    stderr=PIPE
                )
                (stdout, stderr) = branch_command.communicate()[:2]

                if branch_command.returncode != 0:
                    raise ForkRebase(
                        'Failed to run \'git branch\'.\n%s' % stderr
                    )

                # Parse out the current branch
                for line in stdout.decode('utf-8').split('\n'):
                    matches = branches_re.search(line)
                    if matches:
                        self.current_branch = matches.group('name')

            except CalledProcessError:
                raise ForkRebase('Could not find the current branch.')

        return self.current_branch

    def create_remote(self, name, repopath):
        """
        Defines a remote repository
        """
        os.chdir(self.dirname)
        try:
            # Run the git remote command
            remote_command = Popen(
                ['git', 'remote', 'add', name, repopath],
                stdout=PIPE,
                stderr=PIPE
            )
            (stdout, stderr) = remote_command.communicate()[:2]

            if remote_command.returncode != 0:
                raise ForkRebase('Failed to run \'git remote\'.\n%s' % stderr)

        except CalledProcessError:
            raise ForkRebase('Could not find the current remote.')
        self.remotes = None
        self.get_remotes()
        os.chdir(self.basedir)

    def push_master(self):
        """
        Pushs master against upstream/master
        """
        os.chdir(self.dirname)
        try:
            # Run the git push command
            push_command = Popen(
                ['git', 'push', '-f', 'origin', 'master'],
                stdout=PIPE,
                stderr=PIPE
            )
            (stdout, stderr) = push_command.communicate()[:2]

            if push_command.returncode != 0:
                raise ForkRebase('Failed to run \'git push\'.\n%s' % stderr)

        except CalledProcessError:
            raise ForkPush('Could not find the current push.')
        os.chdir(self.basedir)

    def update_submodules(self):
        """
        Updates submodules
        """
        os.chdir(self.dirname)

        try:
            # Run the git submodule command
            submodule_command = Popen(
                ['git', 'submodule', 'init'],
                stdout=PIPE,
                stderr=PIPE
            )
            (stdout, stderr) = submodule_command.communicate()[:2]

            if submodule_command.returncode != 0:
                raise ForkRebase('Failed to run \'git submodule init\'.\n%s' % stderr)

        except CalledProcessError:
            raise ForkRebase('Could not initialize submodules')

        try:
            # Run the git submodule command
            submodule_command = Popen(
                ['git', 'submodule', 'update'],
                stdout=PIPE,
                stderr=PIPE
            )
            (stdout, stderr) = submodule_command.communicate()[:2]

            if submodule_command.returncode != 0:
                raise ForkRebase('Failed to run \'git submodule update\'.\n%s' % stderr)

        except CalledProcessError:
            raise ForkRebase('Could not initialize submodules')
        os.chdir(self.basedir)

    def rebase_master(self):
        """
        Rebases master against upstream/master
        """
        os.chdir(self.dirname)
        try:
            # Run the git rebase command
            rebase_command = Popen(
                ['git', 'rebase', 'upstream/master'],
                stdout=PIPE,
                stderr=PIPE
            )
            (stdout, stderr) = rebase_command.communicate()[:2]

            if rebase_command.returncode != 0:
                raise ForkRebase('Failed to run \'git rebase\'.\n%s' % stderr)

        except CalledProcessError:
            raise ForkRebase('Could not rebase master against upstream')
        os.chdir(self.basedir)

    def fetch_remote(self, name):
        """
        Run fetch for the remote repo
        """
        os.chdir(self.dirname)
        try:
            # Run the git fetch command
            remote_command = Popen(
                ['git', 'fetch', '--prune', name],
                stdout=PIPE,
                stderr=PIPE
            )
            (stdout, stderr) = remote_command.communicate()[:2]

            if remote_command.returncode != 0:
                raise ForkRebase('Failed to run \'git fetch\'.\n%s' % stderr)

        except CalledProcessError:
            raise ForkRebase('Could not find the current remote.')
        os.chdir(self.basedir)

    def __str__(self):
        """
        Returns string representation of a RepoFork
        """
        representation =\
            "Fork Dir: %s\n"\
            "Base Dir: %s\n"\
            "Current Branch: %s\n"\
            % (self.dirname, self.basedir, self.current_branch)

        representation += "Remotes:\n"

        for url, name in self.remotes.items():
            representation += "%s\t%s\n" % (name, url)

        return representation

class App(object):
    """
    Works out which directories are git repositories
    and presents a GUI to help rebase them.
    """

    def __init__(self):
        """
        Run the application
        """
        # Record the starting directory so that we can come back after
        # execution
        self.starting_dir = os.getcwd()

        # Parsed arguments will go into here
        self.args = None
        self.config_file = None
        self.parse_args()

        # Parse in the configuration file
        self.config = None
        self.parse_config()

        # Set the base working directory appropriately
        os.chdir(self.args.basedir)
        self.basedir = os.path.abspath('.')

        # Import the known repositories
        self.known_repos = {}
        self.define_known_repos()

        # Find forks in the current directory
        self.forks = {}
        self.sorted_fork_names = []
        self.find_forks()

        # Find the common upstream, if there is one
        self.upstream = None
        self.find_upstream()

        # Check that all branches are master
        for name, fork in self.forks.items():
            if fork.get_current_branch() != 'master':
                raise ForkRebase(
                    'Fork %s (%s) is on branch %s, not master'\
                    % (name, fork.dirname, fork.get_current_branch())
                )

        # Initialise ttk
        self.root = Tk()

        # Initialise GUI data elements
        self.repotable = None
        self.tablelines = {}
        self.quit_button = None
        self.rebase_button = None

        # Run the GUI
        self.run()

        # Change back to calling directory
        os.chdir(self.starting_dir)


    def find_forks(self):
        """
        Finds the directories under the current working directory
        and checks that they are git repositories
        """
        # Get a list of the directories within the base dir and create a new
        # RepoFork object.
        for dirname in [\
            dirname for dirname in os.listdir()\
            if os.path.isdir(dirname)\
        ]:
            self.forks[dirname] = RepoFork(self.basedir, dirname)

        # Create a sorted list of the fork names
        self.sorted_fork_names = sorted(self.forks.keys())

    def define_known_repos(self):
        """
        Returns a list of known repos that are managed, and their upstream
        masters

        NOTE: The script must already have changed into
        """
        # Define the repository paths and names
        for repo_name in self.config.sections():
            self.known_repos[self.config[repo_name]['url']] = repo_name

    def find_upstream(self):
        """
        Find the common upstream remote, error out if there are more than one.
        """
        # Check each fork to see if there is an upstream remote
        for name, fork in self.forks.items():
            temp_remotes = fork.get_remotes()
            if 'upstream' in temp_remotes:
                if self.upstream and temp_remotes['upstream'] != self.upstream:
                    raise ForkRebase(
                        'Found more than one upstream: %s and %s'\
                        % (self.upstream, temp_remotes['upstream'])
                    )
                else:
                    self.upstream = temp_remotes['upstream']

        # Set our repo name
        if not self.upstream:
            # We haven't found a single upstream!
            raise ForkRebase('No upstream remote found in any forks')

        if self.upstream not in self.known_repos:
            # Set an unknown repo marker to display in the GUI
            self.known_repos[self.upstream] = 'Unknown Repo'

    def parse_config(self):
        """
        Parse in the configuration file containing known upstream repos.
        """
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    def parse_args(self):
        """
        Get the arguments from the command line
        """

        # Top level parser, contains common options
        parser = argparse.ArgumentParser()

        # Base working directory for finding forks
        parser.add_argument(
            '-b',
            '--basedir',
            default='.',
            help=\
                'Directory that contains the clones of the forked '\
                'repositories.'
        )

        # Path to the configuration ini file
        parser.add_argument(
            '-c',
            '--config',
            default='config.ini',
            help=\
                'INI file containing the known repositories.'\
                'If path starts with /, it is regarded as an absolute '\
                'path.'\
                'Config file is as following:'\
                '[Repository Title]'\
                'url = <url to upstream git repo>'
        )

        # Actually read in the arguments from the command line
        self.args = parser.parse_args()

        # Check that base directory exists
        if not os.path.isdir(self.args.basedir):
            raise ForkRebase(
                'Directory ' + self.args.basedir + ' is not a directory\n'
            )

        # Check config file.
        if self.args.config[0] in ['/', '.']:
            # We have an absolute page
            self.config_file = self.args.config
        else:
            # Path relative to the basedir
            self.config_file = '%s/%s' % (self.args.basedir, self.args.config)

        if not os.path.isfile(self.config_file):
            print('Config file %s does not exist\n' % self.config_file)
            self.quit(1)

    @classmethod
    def quit(cls, exitcode=0):
        """
        Quits the current application
        """
        sys.exit(exitcode)

    def set_repo_status(self, name, status):
        """
        Updates the status of the given repo name in the repotable
        """
        self.repotable.set(
            self.tablelines[name],
            'status',
            status
        )
        self.root.update()

    def set_line_colour(self, name, colour):
        """
        Set the colour of a line in the repo table
        """
        self.repotable.tag_configure(
            name,
            foreground=colour
        )
        self.root.update()

    def disable_buttons(self):
        """
        Disable Quit and Rebase Buttons
        """
        self.quit_button['state'] = 'disabled'
        self.rebase_button['state'] = 'disabled'

    def enable_buttons(self):
        """
        Enable Quit and Rebase Buttons
        """
        self.quit_button['state'] = 'enabled'
        self.rebase_button['state'] = 'enabled'

    def rebase(self):
        """
        Rebases the using the given options
        """
        # Temporarily disable buttons
        self.disable_buttons()

        # Find the list of selected items
        selected_items = self.repotable.selection()
        selected_repo_names = []

        if len(selected_items) != 0:
            # Only rebase the selected repos
            for item in selected_items:
                selected_repo_names.append(self.repotable.item(item)['text'])
        else:
            # Rebase all repos
            selected_repo_names = self.sorted_fork_names

        # Set status a colour
        for name in selected_repo_names:
            self.set_line_colour(name, 'black')
            self.set_repo_status(name, '')

        for name in selected_repo_names:
            fork = self.forks[name]
            self.set_repo_status(name, 'Starting Rebase')

            # Create an upstream if we need one
            if 'upstream' not in fork.get_remotes():
                self.set_repo_status(name, 'Creating upstream')
                try:
                    fork.create_remote('upstream', self.upstream)
                except ForkRebase:
                    self.set_line_colour(name, 'red')
                    continue

            # Fetch latest db for upstream and origin
            for remote in ['upstream', 'origin']:
                self.set_repo_status(name, 'Fetching DB for %s' % remote)
                try:
                    fork.fetch_remote(remote)
                except ForkRebase:
                    self.set_line_colour(name, 'red')
                    continue

            # Rebase the master branch against upstream master
            self.set_repo_status(name, 'Rebasing against upstream/master')
            try:
                fork.rebase_master()
            except ForkRebase:
                self.set_line_colour(name, 'red')
                continue

            # Update submodules
            self.set_repo_status(name, 'Updated submodules')
            try:
                fork.update_submodules()
            except ForkRebase:
                self.set_line_colour(name, 'red')
                continue

            # Push changes to fork
            self.set_repo_status(name, 'Pushing master to origin repo')
            try:
                fork.push_master()
            except ForkRebase:
                self.set_line_colour(name, 'red')
                continue

            self.set_repo_status(name, 'Complete')
            self.set_line_colour(name, 'green')
            self.root.update()

        # Reenable buttons
        self.enable_buttons()


    def double_click(self, event):
        """
        This gets run when an item is double clicked.
        """
        # Run the rebase
        self.rebase()

    def run(self):
        """
        Run the GUI
        """

        # Set up the root window
        self.root.title(
            'Rebasing forks of %s repository'\
            % self.known_repos[self.upstream]
        )
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        mainframe = ttk.Frame(
            self.root,
            padding="3 3 3 3",
            width=5000
        )
        mainframe.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)
        mainframe.grid(
            column=0,
            row=0,
            sticky=(N, W, E, S)
        )

        # Notify of the upstream
        ttk.Label(
            mainframe,
            text='Upstream Repo: %s' % self.upstream
        ).grid(column=1, columnspan=1, row=1, sticky=W)

        self.repotable = ttk.Treeview(
            mainframe,
            columns=('path', 'repository', 'status')
        )
        self.repotable.grid(column=1, columnspan=1, row=2, sticky=(W, E))
        self.repotable.column('path', anchor='w', width=300)
        self.repotable.heading('path', text='Path')
        self.repotable.column('repository', anchor='w', width=400)
        self.repotable.heading('repository', text='Repository')
        self.repotable.column('status', anchor='w', width=200)
        self.repotable.heading('status', text='Status')
        self.repotable.bind('<Double-1>', self.double_click)

        # Insert a line for each of the forks
        for name in sorted(self.forks.keys()):
            fork = self.forks[name]
            self.tablelines[name] = self.repotable.insert(
                '',
                'end',
                text=name,
                values=(
                    fork.dirname,
                    fork.get_remotes()['origin'],
                    ''
                ),
                tags=(name, )
            )

        # ttk.Label(
        #     mainframe,
        #     text=self.startingbranch,
        #     foreground='red').grid(
        #         column=2,
        #         row=1,
        #         sticky=W)

        # # Remote to rebase against
        # ttk.Label(mainframe,
        #           text='Rebase Against:')\
        #     .grid(column=1, row=2, sticky=W)

        # cb1 = ttk.Combobox(mainframe,
        #                    textvariable=self.rebaseremote,
        #                    values=self.remotenames,
        #                    state='readonly')
        # cb1.grid(column=2,
        #          row=2,
        #          sticky=W)

        # # If upstream exists, set it to the default
        # if 'upstream' in self.remotenames:
        #     cb1.set('upstream')
        # else:
        #     cb1.current(0)

        # # If we are not on master, see if user wants to
        # # rebase the current branch as well
        # ttk.Label(mainframe,
        #           text='Rebase Current Branch?')\
        #           .grid(column=1,
        #                 row=3,
        #                 sticky=W)
        # cb2 = ttk.Checkbutton(mainframe,
        #                       variable=self.rebasecurrentbranch)
        # cb2.grid(column=2, row=3, sticky=E)

        # # If the default branch is master, set it to 1, and
        # # make it readonly
        # if self.startingbranch == 'master':
        #     self.rebasecurrentbranch.set(1)
        #     cb2.configure(state='disabled')

        # # Push to our origin after rebase?
        # ttk.Label(mainframe,
        #           text='Push to Origin?')\
        #           .grid(column=1, row=4, sticky=W)
        # cb3 = ttk.Checkbutton(mainframe,
        #                       variable=self.pushtoorigin)
        # cb3.grid(column=2,
        #          row=4,
        #          sticky=E)

        # # Separator
        # ttk.Separator(mainframe).grid(
        #     column=1,
        #     row=5,
        #     sticky=(W, E),
        #     columnspan=2
        # )

        # # Status bar
        # ttk.Label(mainframe,
        #           textvariable=self.currentstatus)\
        #           .grid(
        #               column=1,
        #               row=6,
        #               sticky=W,
        #               columnspan=2
        #           )

        # # Separator
        # ttk.Separator(mainframe).grid(
        #     column=1,
        #     row=7,
        #     sticky=(W, E),
        #     columnspan=2
        # )

        # Add buttons at the bottom
        self.quit_button = ttk.Button(
            mainframe,
            text='Quit',
            command=self.quit
        )
        self.quit_button.grid(column=1, row=3, sticky=W)

        self.rebase_button = ttk.Button(
            mainframe,
            text='Rebase',
            command=self.rebase
        )
        self.rebase_button.grid(column=1, row=3, sticky=E)

        # for x in range(2):
        #     mainframe.columnconfigure(x, weight=1)
        # for y in range(3):
        #     mainframe.rowconfigure(y, weight=1)
        mainframe.columnconfigure(1, weight=1, minsize=1000)

        self.root.mainloop()

if __name__ == '__main__':

    app = App()
