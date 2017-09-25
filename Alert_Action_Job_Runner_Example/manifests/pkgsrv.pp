class splunk::pkgsrv (
  String $pkgname,
  String $pkgver,
  String $srvname,
  ) {
    if $pkgver {
      $ensure = $pkgver
    }
    else {
      $ensure = 'present'
    }

    package { $pkgname :
      ensure => $ensure,
    }

    service { $srvname :
      ensure  => running,
      enable  => true,
      require => Package[$pkgname],
    }
  }
