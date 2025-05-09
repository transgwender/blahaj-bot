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

      token = mkOption {
        type = types.path;
        description = ''
          Path to the token secret
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
        ExecStart = "+${pkgs.blahaj-bot}/bin/bot ${cfg.token} -u";
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