all: _layout.so

_layout.so: layout.c
	gcc -std=c99 -O3 -shared -o _layout.so layout.c
