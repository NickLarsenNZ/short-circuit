import logging
from graph.graph import Nand, Wire

logger = logging.getLogger()

class Grid:
    def __init__(self):
        self.tiles = [[None] * 20 for y in range(20)]

    def to_world(self):
        """
        Converts the grid into a graph representation
        """
        pass

    def find_components(self):
        """
        Performs connected-component labeling to find groups of wires

        https://en.wikipedia.org/wiki/Connected-component_labeling#Two-pass
        """

        # Map of tiles to labels
        tile_lookup = {}
        # Map of labels to tiles
        label_lookup = {}
        # Map of labels to labels for later merging
        merge = {}
        # Map of NANDs
        nands = []

        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[y])):
                me = (x, y)
                tile = self.tiles[y][x]

                if isinstance(tile, Nand):
                    nands.append(me)

                elif isinstance(tile, Wire):
                    left = (x-1, y)
                    top = (x, y-1)

                    try:
                        if isinstance(self.get(*left), Wire):
                            label = tile_lookup[left]
                            label_top = tile_lookup[top]  # can cause IndexError
                            if label_top != label:
                                merge[min(label_top, label)] = max(label_top, label)
                        elif isinstance(self.get(*top), Wire):
                            label = tile_lookup[top]
                            label_left = tile_lookup[left]  # can cause IndexError
                            if label_left != label:
                                merge[min(label_left, label)] = max(label_left, label)
                        else:
                            label = len(label_lookup)
                    except KeyError:
                        pass
                    tile_lookup[me] = label
                    label_lookup[label] = label_lookup.get(label, []) + [me]

        # Perform merges
        for k, v in merge.items():
            label_lookup[k] = label_lookup[k] + label_lookup[v]
            for t in label_lookup[v]:
                tile_lookup[t] = k
            del label_lookup[v]

        return {
                'label_lookup': label_lookup,
                'tile_lookup': tile_lookup,
                'nands': nands
                }

    def get(self, x: int, y: int):
        """
        Useful in connected-component labeling so we don't go out of
        bounds
        """
        try:
            return self.tiles[y][x]
        except IndexError:
            return GROUND
