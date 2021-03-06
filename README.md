Sparked
-------

Like the Twisted asynchronous network framework, Sparked is a python
library and an application runner in one. Some of its features follow
here:

 * Robust startup and restart of the program; if it crashes, it's
   started again.

 * Logging: keeps a rotated logfile for debugging purposes.

 * Pidfile management for making sure your app starts only once.

 * A GUI status window (based on GTK) for monitoring the state of the
   application and the state of the system (network, power supply,
   ...). Easy to add your own monitors.

 * Fullscreen graphics display for creating interactive displays,
   based on the clutter library.

 * Eventing system for broadcasting messages between sparked
   components.

 * A state machine for guiding the application through different
   states, with callback functions.

 * Possibility to run the sparked application as a twisted plugin for
   server applications, including a generic init.d startup script.

 * Plug-and-play support for hardware: automatically start and stop
   parts of the program when hardware is added or removed.

