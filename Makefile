# $FreeBSD$

PORTNAME=	pfSense-pkg-statusb_mon
DISTVERSION=	0.7.1
CATEGORIES=	sysutils
MASTER_SITES=	# empty
DISTFILES=	# empty
EXTRACT_ONLY=	# empty

MAINTAINER=	sgrimes@gmail.com
COMMENT=	pfSense package statusb_mon

LICENSE=	APACHE20

# Not sure how to correctly set the python dependency. This /seems/ to work
RUN_DEPENDS=	${LOCALBASE}/bin/dpinger:net/dpinger \
		${LOCALBASE}/lib/python3.7/site-packages/serial/__init__.py:comms/py-serial

NO_BUILD=	yes
NO_MTREE=	yes

SUB_FILES=	pkg-install pkg-deinstall
SUB_LIST=	PORTNAME=${PORTNAME}

do-extract:
	${MKDIR} ${WRKSRC}

do-install:
	${MKDIR} ${STAGEDIR}${PREFIX}/bin
	${MKDIR} ${STAGEDIR}${PREFIX}/pkg
	${MKDIR} ${STAGEDIR}/etc/inc/priv
	${MKDIR} ${STAGEDIR}${DATADIR}
	${INSTALL_DATA} ${FILESDIR}${PREFIX}/pkg/statusb_mon.xml \
		${STAGEDIR}${PREFIX}/pkg
	${INSTALL_DATA} ${FILESDIR}${PREFIX}/pkg/statusb_mon.inc \
		${STAGEDIR}${PREFIX}/pkg
	${INSTALL_SCRIPT} ${FILESDIR}${PREFIX}/bin/statusb_mon.py \
		${STAGEDIR}${PREFIX}/bin
	${INSTALL_SCRIPT} ${FILESDIR}${PREFIX}/bin/pseudosock.py \
		${STAGEDIR}${PREFIX}/bin
	${INSTALL_DATA} ${FILESDIR}/etc/inc/priv/statusb_mon.priv.inc \
		${STAGEDIR}/etc/inc/priv
	${INSTALL_DATA} ${FILESDIR}${DATADIR}/info.xml \
		${STAGEDIR}${DATADIR}
	@${REINPLACE_CMD} -i '' -e "s|%%PKGVERSION%%|${PKGVERSION}|" \
		${STAGEDIR}${DATADIR}/info.xml
	@${REINPLACE_CMD} -i '' -e "s|%%PKGVERSION%%|${PKGVERSION}|" \
			${STAGEDIR}${PREFIX}/bin/statusb_mon.py
.include <bsd.port.mk>
