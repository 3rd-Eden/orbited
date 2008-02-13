from orbited.router import router, CSPDestination


router.register(CSPDestination, '/_/csp')
router.register(StaticDestination, '/_/csp/static', '[orbited-static]')
