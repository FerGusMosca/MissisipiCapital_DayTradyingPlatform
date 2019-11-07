from sources.framework.business_entities.securities.security import *

class SecurityToTrade():

    def __init__(self, security,shares,active):
        self.Security = security
        self.Shares= shares
        self.Active=active
