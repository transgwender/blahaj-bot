{
  config,
  pkgs,
  lib ? pkgs.lib,
  ...
}:

with lib;

let

  cfg = config.services.blahaj-bot;

in

{
  # Interface
  options = {
    services.blahaj-bot = rec {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = ''
          Whether to run the blahaj-bot
        '';
      };

      config = mkOption {
        type = types.path;
        description = ''
          Path to the config
        '';
      };

      dbPort = mkOption {
        type = types.int;
        description = ''
          Port to use for database
        '';
      };
    };
  };

  # Implementation
  config = mkIf cfg.enable {

    users.extraGroups.blahaj-bot = {};
    users.extraUsers.blahaj-bot = {
      description = "blahaj-bot";
      group = "blahaj-bot";
      # home = baseDir;
      isSystemUser = true;
      useDefaultShell = true;
    };


    environment.systemPackages = [ pkgs.blahaj-bot ];

    systemd.services.blahaj-bot = {
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        Restart = "on-failure";
        ExecStart = "+${pkgs.blahaj-bot}/bin/bot ${cfg.config} ${builtins.toString cfg.dbPort} -u";
        User = "blahaj-bot";
        # DynamicUser = "yes";
        RuntimeDirectory = "blahaj-bot";
        RuntimeDirectoryMode = "0755";
        StateDirectory = "blahaj-bot";
        StateDirectoryMode = "0700";
        CacheDirectory = "blahaj-bot";
        CacheDirectoryMode = "0750";
        StandardOutput = "journal";
      };
    };
  };
}