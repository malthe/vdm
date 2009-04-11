'''
About
=====

Versioned Domain Model (vdm) is a package which allows you to 'version' your
domain model in the same way that source code version control systems such as
subversion allow you version your code. In particular, versioned domain model
versions a complete model and not just individual domain objects (for more on
this distinction see below).

At present the package is provided as an extension to SQLAlchemy and SQLObject.


Copyright and License
=====================

(c) 2007-2009 The Open Knowledge Foundation

Licensed under the MIT license:

  <http://www.opensource.org/licenses/mit-license.php>


Authors
=======

Rufus Pollock <rufus [at] rufuspollock [dot] org>


A Full Versioned Domain Model
=============================

To permit 'atomic' changes involving multiple objects at once as well as to
facilitate domain object traversal it is necessary to introduce an explicit
'Revision' object to represent a single changeset to the domain model.

One also needs to introduce the concept of 'State'. This allows us to make
(some) domain objects stateful, in particular those which are to be versioned
(State is necessary to support delete/undelete functionality as well as to
implement versioned many-to-many relationships).

For each original domain object that comes versioned we end up with 2 domain
objects:

  * The 'continuity': the original domain object.
  * The 'version/revision': the versions/revisions of that domain object.

Often a user will never need to be concerned (explicitly) with the
version/revision object as they will just interact with the original domain
object, which will, where necessary, 'proxy' requests down to the
'version/revision'.

To give a flavour of all of this here is a pseudo-code example::

    # We need a session of some kind to track which objects have been changed
    # In SQLAlchemy can use its Session object
    session = get_session_in_some_way()
    
    # Our Revision object
    rev1 = Revision(author='me')
    # Associate revision with session
    # Any given session will have a single associated revision
    session.revision = rev1
    
    # Book and Author are domain objects which has been made versioned using this library
    # Note the typo!
    b1 = Book(name='warandpeace', title='War and Peacee')
    b2 = Book(name='annakarenina', title='Anna')
    # Note the duplicate!
    b3 = Book(name='warandpeace')
    a1 = Author(name='tolstoy')

    # this is just shorthand for ending this revision and saving all changes
    # this may vary depending on the implementation
    rev1.commit()
    timestamp1 = rev1.timestamp

    # some time later
    rev2 = Revision(author='me')
    session.revision = rev2

    b1 = Book.get(name='warandpeace')
    # correct typo
    b1.title = 'War and Peace'
    # add the author
    a1 = Author.get(name='tolstoy')
    b1.authors.append(a1)
    # duplicate item so delete
    b3.delete()
    rev2.commit()

    # some time even later
    rev1 = Revision.get(timestamp=timestamp1)
    b1 = Book.get(name='warandpeace') 
    b1 = b1.get_as_of(rev1)
    assert b1.title == 'War and Peacee'
    assert b1.authors == []
    # etc


Code in Action
--------------

To see some real code in action take a look at::

    vdm/sqlalchemy/demo.py
    vdm/sqlalchemy/demo_test.py

WARNING: the SQLObject code is no longer actively maintained.

    vdm/sqlobject/demo.py
    vdm/sqlobject/demo_test.py


General Conceptual Documentation
================================

A great starting point is Fowler's *Patterns for things that change with time*:

  <http://www.martinfowler.com/ap2/timeNarrative.html>

In particular Temporal Object:

  <http://www.martinfowler.com/ap2/temporalObject.html>

Two possible approaches:

  1. (simpler) Versioned domain objects are versioned independently (like a
     wiki). This is less of a versioned 'domain model' and more of plain
     versioned domain objects.
  2. (more complex) Have explicit 'Revision' object and multiple objects can be
     changed simultaneously in each revision (atomicity). This is a proper
     versioned *domain model*.

Remark: using the first approach it is:

  * Impossible to support versioning of many-to-many links between versioned
    domain objects.
  * Impossible to change multiple objects 'at once' -- that is as part of
    one atomic change
  * Difficult to support domain model traversal, that is the ability to
    navigate around the domain model at a particular 'revision'/point-in-time.
  * More discussions of limitations can be found in this thread [1].

[1]:<http://groups.google.com/group/sqlelixir/browse_thread/thread/50aee902ce3555fb/>

The versioned domain model (vdm) package focuses on supporting the second case
(this obviously includes the first one as a subcase) -- hence the name.


Use Cases
---------

SA = Implemented in SQLAlchemy
SO = Implemented in SQLObject (no longer maintained)

1. (SA,SO) CRUD for a simple versioned object (no references other than HasA)

2. (SA,SO) Many-2-Many and many-2-one relationships where one or both of the
objects are versioned.

3. (SA,SO) Undelete for the above.

4. (SA,SO) Purge for the above.

5. (SA, SO) Support for changing multiple objects in a single commit.

6. (SA) Consistent object traversal both at HEAD and "in the past"

7. Concurrency checking:
  1. Simultaneous edits of different parts of the domain model
  2. Simultaneous edits of same parts of domain model (conflict resolution or
     locking)

     1. Alice and Bob both get object X
     2. Bob updates object X and commits (A's X is now out of date)
     3. Alice updates object X and commits
     4. Conflict!!

     This can be resolved in the following ways:

     1. Locking 
     2. Merging

     Rather than summarize all situations just see Fowler on concurrency

8. Support for pending updates (so updates must be approved before being visible)
  1. A non-approved user makes a change
  2. This change is marked as pending
  3. This change is notified to a moderator
  4. A moderator either allows or disallows the change
'''
__version__ = '0.4'
__description__ = 'A versioned domain model framework.'
