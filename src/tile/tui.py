import logging
import sys
from tile.grid import Grid
from graph.graph import Nand, Wire

from blessed import Terminal
from blessed.formatters import FormattingString
from blessed.keyboard import Keystroke

logger = logging.getLogger()

class TermUI:
    def handle_inputs(self, inp: Keystroke):
        if inp in 'q' or inp.name == 'KEY_ESCAPE':
            return {'exit': True}

        if inp in 'wk':
            return {'move': (0,-1)}
        elif inp in 'sj':
            return {'move': (0,1)}
        elif inp in 'ah':
            return {'move': (-1,0)}
        elif inp in 'dl':
            return {'move': (1,0)}
        elif inp in ' n':
            return {'toggle': {'direction': 1}}
        elif inp == 'p':
            return {'toggle': {'direction': -1}}

        elif inp == 'z':
            return {'debug': True}
        elif inp == 'x':
            return {'save': {'filename': 'output/layout.shs'}}
        else:
            return {'no_op': True}

    def __init__(self, grid: Grid):
        self.t = Terminal()
        self.grid = grid
        self.cursor_pos = (0,0)

        # Used for rendering tiles
        self.glyphs = {
            'ground': '.',
            'wire': '+',
            'nand_up': '^',
            'nand_down': 'v',
            'nand_left': '<',
            'nand_right': '>',
        }

        logger.info("----------------------------------")
        logger.info("Terminal colors: %d", self.t.number_of_colors)
        logger.info("Terminal size: %dx%d", self.t.width, self.t.height)

    def editor_loop(self):
        while True:
            self.render()

            # Get input
            inp = self.t.inkey()
            logger.debug('Key Input: ' + repr(inp))

            action = self.handle_inputs(inp)

            move = action.get('move')
            toggle = action.get('toggle')
            save = action.get('save')

            if action.get('exit'):
                break
            elif action.get('debug'):
                # Print out a bunch of debug stuff
                logger.debug('This is the debug string.')
                # Iterate through the entire grid, print out all the labels.
                for wire in self.grid.get_all_wire():
                    logger.debug(wire)

            elif move:
                self.cursor_pos = (
                    self.cursor_pos[0] + move[0],
                    self.cursor_pos[1] + move[1],
                )
                logger.debug('Cursor pos: %s', self.cursor_pos)
            elif toggle:
                # Toggle between tile pieces
                x, y = self.cursor_pos
                current = self.grid.tiles[y][x]
                new = None if current else Wire()
                self.grid.change_tile((x, y), new)
                # Tile((current.value + toggle['direction']) % len(Tile))
            elif save:
                filename = save['filename']
                logger.info(f'Writing grid state to file: {filename}')
                with open(filename, 'w') as f:
                    self.grid.serialize(f)


    def render(self):
        print(self.t.clear())

        components = self.grid.find_components()

        # Render the grid
        print(self.t.move(0, 0), end='')
        for y in range(len(self.grid.tiles)):
            for x in range(len(self.grid.tiles[y])):
                # Get the glyph which represents this tile
                # glyph = self.glyphs.get(self.grid.tiles[y][x], '?')
                glyph = self.t.color(15)('.')
                if isinstance(self.grid.tiles[y][x], Wire):
                    color = components['tile_lookup'][(x,y)] + 1
                    glyph = self.t.color(color)('+')
                print(self.t.color(15)(glyph), end='')
            print()

        logger.info(self.grid.find_components())

        # Can change this to be smarter if we ever have a viewport
        print(self.t.move(self.cursor_pos[1], self.cursor_pos[0]), end='')
        sys.stdout.flush()

    def start(self):
        # Ready the screen for drawing
        print(self.t.enter_fullscreen())

        # Handle input immediately
        with self.t.cbreak():

            # Enter the main game loop
            self.editor_loop()

        print(self.t.exit_fullscreen())
