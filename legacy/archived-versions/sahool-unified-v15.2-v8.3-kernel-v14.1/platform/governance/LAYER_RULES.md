# Layer Rules v15.2

## Layer 2 (Signal Producer)
- No public APIs (only internal endpoints allowed)
- No Redis access
- Can publish: internal.*, weather.*, image.*, ndvi.*, astro.*

## Layer 3 (Decision)
- Public APIs allowed
- Redis access allowed
- Can consume: all
- Cannot publish: internal.*

## Layer 4 (Action)
- Public APIs allowed
- Redis access allowed
- Can consume: all
- Cannot publish: internal.*, weather.*, image.*, ndvi.*, astro.*
