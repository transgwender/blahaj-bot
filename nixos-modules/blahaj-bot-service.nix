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

    users.groups.blahaj-bot = {};
    users.users.blahaj-bot = {
      description = "blahaj-bot";
      # home = baseDir;
      isSystemUser = true;
      useDefaultShell = true;
      group = "blahaj-bot";
    };
    environment.systemPackages = [ pkgs.blahaj-bot ];

    systemd.services.blahaj-bot = {
      wantedBy = [ "multi-user.target" ];
      serviceConfig = let pkg = self.packages.${pkgs.system}.default;
      in {
        Restart = "on-failure";
        ExecStart = "${pkg}/bin/bot ${cfg.token}";
        User = "blahaj-bot";
        RuntimeDirectory = "blahaj-bot";
        RuntimeDirectoryMode = "0755";
        StateDirectory = "blahaj-bot";
        StateDirectoryMode = "0700";
        CacheDirectory = "blahaj-bot";
        CacheDirectoryMode = "0750";
      };
    };
  };
}