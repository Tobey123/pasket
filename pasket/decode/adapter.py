from functools import partial
import re
import logging

import lib.visit as v
import lib.const as C

from .. import util
from ..meta import methods, class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression


class Adapter(object):

  __aux_name = C.ADP.AUX

  ## hole assignments for roles
  ## glblInit_accessor_????,StmtAssign,accessor_???? = n
  regex_role = r"(({})_(\S+)_(\d+)_{}).* = (\d+)$".format('|'.join(C.adp_roles), __aux_name)

  @staticmethod
  def simple_role_of_interest(msg):
    return re.match(Adapter.regex_role, msg)

  # add a mapping from role variable to its value chosen by sketch
  def add_simple_role(self, msg):
    m = re.match(Adapter.regex_role, msg)
    v, n = m.group(1), m.group(5)
    self._role[v] = n

  # initializer
  def __init__(self, output_path, adp_conf):
    self._output = output_path
    self._demo = util.pure_base(output_path)
    self._adp_conf = adp_conf

    self._cur_mtd = None
    self._role = {} # { v : n }

    # method roles
    self._adapter = {} # { Aux... : Adapter }
    self._adaptee = {} # { Aux... : Adaptee }
    
    # interpret the synthesis result
    with open(self._output, 'r') as f:
      for line in f:
        line = line.strip()
        try:
          items = line.split(',')
          func, kind, msg = items[0], items[1], ','.join(items[2:])
          if Adapter.simple_role_of_interest(msg): self.add_simple_role(msg)
        except IndexError: # not a line generated by custom codegen
          pass # if "Total time" in line: logging.info(line)

  @property
  def demo(self):
    return self._demo

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  # adapter code
  @staticmethod
  def def_adapter(adapter, adaptee, adpfield):
    logging.debug("adding adapter code into {}".format(repr(adapter)))
    rcv = u"{}_{}_{}".format(C.ADP.FLD, adpfield.id, adapter.clazz.name)
    adpe_call = u"{}.{}();".format(rcv, adaptee.name)
    adapter.body = to_statements(adapter, adpe_call)

  # add a private field
  @staticmethod
  def add_prvt_fld(acc, inst, typ, num):
    name = u'_'.join([C.ADP.FLD, unicode(num), acc.name])
    fld = acc.fld_by_name(name)
    if not fld:
      logging.debug("adding private field {} for {} of type {}".format(str(num), acc.name, typ))
      fld = Field(clazz=acc, typ=typ, name=name)
      acc.add_fld(fld)
    setattr(acc, C.ACC.CONS+"_"+inst+"_"+str(num), fld)

  # constructor code
  @staticmethod
  def def_constructor(mtd, acc):
    logging.debug("adding constructor code into {}".format(repr(mtd)))
    for i, (ty, nm) in enumerate(mtd.params):
      init = u"{}_{}_{} = {};".format(C.ADP.FLD, unicode(i), acc.name, nm)
      mtd.body += to_statements(mtd, init)


  @v.when(Template)
  def visit(self, node):
    def find_role(lst, aux_name, role):
      try:
        _id = self._role['_'.join([role, aux_name])]
        return lst[int(_id)]
      except KeyError: return None

    aux_name = self.__aux_name
    aux = class_lookup(aux_name)

    # find and store method roles
    find_mtd_role = partial(find_role, methods(), aux_name)
      
    adpt, adpe, adpf = map(find_mtd_role, C.adp_roles)
    logging.debug("adapter: {}".format(repr(adpt)))
    logging.debug("adaptee: {}".format(repr(adpe)))

    adpt = {}
    adpe = {}
    adpf = {}
    for key in self._adp_conf.iterkeys():
      adpt[key] = {}
      adpe[key] = {}
      adpf[key] = {}
      for x in range(self._adp_conf[key][0]):
        adpt[key][x] = find_mtd_role('_'.join([C.ADP.ADPT, key, str(x)]))
        adpe[key][x] = find_mtd_role('_'.join([C.ADP.ADPE, key, str(x)]))
        adpf[key][x] = find_mtd_role('_'.join([C.ADP.FLD, key, str(x)]))

    self._adapter[aux.name] = adpt
    self._adaptee[aux.name] = adpe

    # insert code snippets for adapter
    for key in self._adp_conf.iterkeys():
      for x in range(self._adp_conf[key][0]): 
        if adpt[key][x]: 
          adpt_cls = adpt[key][x].clazz
          for init in adpt_cls.inits:
            for n, t in enumerate(init.param_typs):
              Adapter.add_prvt_fld(adpt_cls, adpt_cls.name, t, n)
            Adapter.def_constructor(init, adpt_cls)

          Adapter.def_adapter(adpt[key][x], adpe[key][x], adpf[key][x])

    # remove Aux class
    node.classes.remove(aux)

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    self._cur_mtd = node

  @v.when(Statement)
  def visit(self, node):
    if node.kind == C.S.EXP and node.e.kind == C.E.CALL:
      call = unicode(node)
      if call.startswith(C.ADP.AUX):
        logging.debug("removing {}".format(call))
        return []

    return [node]

  @v.when(Expression)
  def visit(self, node): return node

