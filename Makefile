prefix=/usr

all:

clean:
	find . -name *.pyc | xargs rm -f

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/bin"
	install -m 0755 config-sync "$(DESTDIR)/$(prefix)/bin"

	install -d -m 0755 "$(DESTDIR)/$(prefix)/lib/config-sync"
	cp -r lib/* "$(DESTDIR)/$(prefix)/lib/config-sync"
	find "$(DESTDIR)/$(prefix)/lib/config-sync" -type f | xargs chmod 644
	find "$(DESTDIR)/$(prefix)/lib/config-sync" -type d | xargs chmod 755

uninstall:
	rm -Rf "$(DESTDIR)/$(prefix)/bin/config-sync"
	rm -Rf "$(DESTDIR)/$(prefix)/lib/config-sync"

.PHONY: all clean install uninstall

