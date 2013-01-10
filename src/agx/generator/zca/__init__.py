import zcagenerator


def register():
    """Register this generator.
    """
    import agx.generator.zca
    from agx.core.config import register_generator
    register_generator(agx.generator.zca)
