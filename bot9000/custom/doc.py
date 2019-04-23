
docs = {
    'FR': {
        'ContextCapsule': {
            '__self': """##ContextCapsule
        	- Contiens toutes les informations contextuelles, comme le message de la commande, le channel où il a été envoyé, le serveur actuel, l'expéditeur, ...
        	- Passé comme unique argument à la fonction de commande""",

            'message': """###ContextCapsule.message()
    		- **Retourne** : Le message qui a appelé la commande (objet `MessageCapsule`)""",

            'channel': """###ContextCapsule.channel()
    		- **Retourne** : Le channel où la commande a été envoyée (objet `ChannelCapsule`)""",

            'server': """###ContextCapsule.server()
    		- **Retourne** : Le serveur où la commande a été envoyée (objet `ServerCapsule`)""",

            'player': """###ContextCapsule.player()
    		- **Retourne** : Le joueur qui a envoyé la commande. Retourne un objet `PlayerCapsule` complet si c'est un joueur enregistré, sinon retourne un faux objet avec discordid() = None et le langage par défaut du groupe""",

            'corporation': """###ContextCapsule.corporation()
    		- **Retourne** : L'objet `CorporationCapsule` correspondant au joueur, ou None s'il n'est pas enregistré."""

            'get_role': """###ContextCapsule.get_role(name)
    		- **name** : Le nom du rôle à récupérer
    		- **Retourne** : Le rôle demandé en tant qu'objet `RoleCapsule`, ou None s'il n'existe pas""",

            'get_role_byid': """###ContextCapsule.get_role_byid(id)
    		- **name** : ID du rôle à récupérer
    		- **Returns** : Le rôle demandé en tant qu'objet `RoleCapsule`, ou None s'il n'existe pas""",
    }, 'EN': {
        'ContextCapsule': {
            '__self': """##ContextCapsule
        	- Contains everything related to the command's execution context, like the command message, the current channel, the server, ...
        	- Passed as the only argument to the command's function""",

            'message': """###ContextCapsule.message()
    		- **Returns** : The message that triggered the command (`MessageCapsule` object)""",

            'channel': """###ContextCapsule.channel()
    		- **Returns** : The channel where the command was sent (`ChannelCapsule` object)""",

            'server': """###ContextCapsule.server()
    		- **Returns** : The discord server where the command was sent (`ServerCapsule` object)""",

            'player': """###ContextCapsule.player()
    		- **Returns** : The player who called the command. Returns a full `PlayerCapsule` object if it is a registered player, else returns a dummy object that contains a few default informations (group language, and discordid() = None)""",

            'corporation': """###ContextCapsule.corporation()
    		- **Returns** : The caller's corporation as a `CorporationCapsule` object, or None if the player is not registered."""

            'get_role': """###ContextCapsule.get_role(name)
    		- **name** : Name of the role to find
    		- **Returns** : The role with the given name on the current server, as a `RoleCapsule`, or None if the role is not found""",

            'get_role_byid': """###ContextCapsule.get_role_byid(id)
    		- **name** : ID of the role to find
    		- **Returns** : The role with the given ID on the current server, as a `RoleCapsule`, or None if the role is not found""",
        }
    }
}
