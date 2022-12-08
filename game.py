import random
from copy import deepcopy
from math import sqrt, log
from utils import reshape

class Game:
  def __init__(self, myId, players, myCards, currentTrick, \
               playedCards, trumpSuit, suitLeader, trumpRevealed,\
               valueWon, trumpChooser, bid, bidder):
    '''
    currentTrick -> list []
    players -> list []
    '''
    self.myId = myId
    self.players = players
    self.playerHands = {p: [] for p in [pl for pl in players if pl != self.myId]}
    self.playerHands[myId] = myCards
    self.valueWon = valueWon
    self.currentTrick = currentTrick
    self.currentPlayer = self.myId
    self.playedCards = playedCards
    self.trumpSuit = trumpSuit
    self.trumpRevealed = trumpRevealed
    self.trumpChooser = trumpChooser
    self.suitLeader = suitLeader
    self.bid = bid
    self.bidder = bidder
    self.deal()

  def getDeck(self):
    ranks = ["J", "9", "T", "1", "K", "Q", "8", "7"]
    deck = [rank + suit for rank in ranks for suit in ["S", "D", "H", "C"]]
    return deck

  def getSuit(self, card):
    return card[1]

  def getRank(self, card):
    return card[0:len(card)]

  def deal(self):
    deck = self.getDeck()
    seen_cards = self.playerHands[self.myId] + self.currentTrick + self.playedCards
    distribute = [card for card in deck if card not in seen_cards]
    #determinize
    random.shuffle(distribute)
    for p in [player for player in self.players if player != self.myId]:
      if self.players.index(p) < self.players.index(self.myId):
        self.playerHands[p] = distribute[:(len(self.playerHands[self.myId]) - 1)]
        distribute = distribute[(len(self.playerHands[self.myId]) - 1):]
      else:
        self.playerHands[p] = distribute[:(len(self.playerHands[self.myId]) + 1)]
        distribute = distribute[(len(self.playerHands[self.myId]) + 1):]

    if(not(self.trumpSuit) and not(self.trumpRevealed)):
      plays = reshape(self.playedCards, (len(self.playedCards)//4,4))
      improbable = (card[1] for play in plays for card in play if card[1] != play[0][1])
      probable = [suit for suit in ["S", "D", "H", "C"] if suit not in improbable]
      self.trumpSuit = random.choice(probable)

  def clone(self):
    p = deepcopy(self.players)
    mc = deepcopy(self.playerHands[self.myId])
    ct = deepcopy(self.currentTrick)
    pc = deepcopy(self.playedCards)
    vw = deepcopy(self.valueWon)
    return Game(self.myId, p, mc, ct, pc, self.trumpSuit, self.suitLeader,\
                self.trumpRevealed, vw, self.trumpChooser, self.bid, self.bidder)


  def cloneAndRandomize(self, currentPlayer):
    st = self.clone()
    deck = self.getDeck()
    seen_cards = st.playerHands[self.myId] + st.currentTrick + st.playedCards
    distribute = [card for card in deck if card not in seen_cards]
    random.shuffle(distribute)
    for p in [player for player in self.players if player != self.myId]:
      if self.players.index(p) < self.players.index(self.myId):
        self.playerHands[p] = distribute[:(len(self.playerHands[self.myId]) - 1)]
        distribute = distribute[(len(self.playerHands[self.myId]) - 1):]
      else:
        self.playerHands[p] = distribute[:(len(self.playerHands[self.myId]) + 1)]
        distribute = distribute[(len(self.playerHands[self.myId]) + 1):]
    
    return st

  def getNextPlayer(self, currentPlayer):
    return self.players[(self.players.index(currentPlayer) + 1) % 4]

  def getValue(self, trick):
    values = {"J":3, "9":2, "T":1, "1":1, "K":0, "Q":0, "8":0, "7":0}
    total = 0
    for card in trick:
      total += values[card[0]]
    return total

  def meTrump(self, id):
    return True if id == self.trumpChooser else False

  def doMove(self, move):
    priority = {"J":0, "9":1, "T":2, "1":3, "K":4, "Q":5, "8":6, "7":7}
    self.currentTrick.append(move)
    self.playerHands[self.currentPlayer].remove(move)
    self.currentPlayer = self.getNextPlayer(self.currentPlayer)

    if(len(self.currentTrick) == 4):
      lead_suit = self.getSuit(self.currentTrick[0])
      suitedPlays = [card for card in self.currentTrick if self.getSuit(card) \
                     == lead_suit]
      trumpPlays = []
      if(not(self.meTrump(self.currentPlayer) ^ bool(self.trumpRevealed)) or (not(self.meTrump(self.currentPlayer)) and bool(self.trumpRevealed))):
        trumpPlays = [card for card in self.currentTrick if self.getSuit(card) \
                       == self.trumpSuit]

      sortedPlays = sorted(suitedPlays, key = lambda card: priority[card[0]]) + \
                    sorted(trumpPlays, key = lambda card: priority[card[0]])

      winningCard = sortedPlays[-1]
      #get winners ID
      winner = self.getNextPlayer(self.suitLeader)
      for _ in range(self.currentTrick.index(winningCard)):
        winner = self.getNextPlayer(winner)
      
      self.valueWon[winner] += self.getValue(self.currentTrick)
      self.playedCards += self.currentTrick
      self.currentTrick = []
      self.currentPlayer = winner

      #if self.playerHands[self.currentPlayer] == []:

  def getMoves(self):
    hand = self.playerHands[self.currentPlayer]
    if self.currentTrick == []:
      return hand
    else:
      if (self.trumpSuit and self.trumpRevealed):
        was_trump_revealed_in_this_round = self.trumpRevealed["hand"] == len(self.playedCards)/4 + 1
        did_i_reveal_the_trump = self.trumpRevealed["playerId"] == self.myId
        if was_trump_revealed_in_this_round and did_i_reveal_the_trump:
          trump_suit_cards = [card for card in hand if card[1] == self.trumpSuit]
          if len(trump_suit_cards) > 0:
            return trump_suit_cards
          else:
            return hand
          
      suitedCard = [card for card in hand if card[1] == self.currentTrick[0][1]]
      if suitedCard != []:
        return suitedCard
      else:
        return hand

        

  def getResult(self, playerID):
    partnerIndex = (self.players.index(playerID) + 2) % 4
    partnerId = self.players[partnerIndex]
    opponentId = [self.getNextPlayer(partnerId), self.getNextPlayer(playerID)]

    if self.bidder in [playerID, partnerId]:
      return 1 if(self.valueWon[playerID] + self.valueWon[partnerId])>= self.bid else 0
    else:
      return 1 if(self.valueWon[opponentId[0]] + self.valueWon[opponentId[1]]) < self.bid else 0

class Node:
  def __init__(self, move=None, parent=None, player=None):
    self.move = move
    self.parentNode = parent
    self.childNodes = []
    self.player = player
    self.wins = 0
    self.visits = 0
    self.avails = 1

  def getUntriedMoves(self, legalMoves):
    triedMoves = [child.move for child in self.childNodes]
    return [move for move in legalMoves if move not in triedMoves]

  def UCBSelectChild(self, legalMoves, exploration=0.7):
    legalChildren = [child for child in self.childNodes if child.move in legalMoves]
    s = max(
        legalChildren,
        key=lambda c: float(c.wins) / float(c.visits)
        + exploration * sqrt(log(c.avails) / float(c.visits)),
    )

    for child in legalChildren:
      child.avails += 1
    
    return s

  def addChild(self, m, p):
    n = Node(move = m, parent=self, player=p)
    self.childNodes.append(n)
    return n

  def Update(self, terminalState):
    self.visits += 1
    if self.player is not None:
        self.wins += terminalState.getResult(self.player)


def ISMCTS(rootstate, itermax):
  rootnode = Node()
  for i in range(itermax):
    node = rootnode
    state = rootstate.cloneAndRandomize(rootstate.currentPlayer)
            # Select
    while (
        state.getMoves() != [] and node.getUntriedMoves(state.getMoves()) == []
    ):  # node is fully expanded and non-terminal
        node = node.UCBSelectChild(state.getMoves())
        state.doMove(node.move)

    # Expand
    untriedMoves = node.getUntriedMoves(state.getMoves())
    if untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
        m = random.choice(untriedMoves)
        player = state.currentPlayer
        state.doMove(m)
        node = node.addChild(m, player)  # add child and descend tree

    # Simulate
    while state.getMoves() != []:  # while state is non-terminal
        state.doMove(random.choice(state.getMoves()))

    # Backpropagate
    while (
        node != None
    ):  # backpropagate from the expanded node and work back to the root node
        node.Update(state)
        node = node.parentNode

  return max(
      rootnode.childNodes, key=lambda c: c.visits
  ).move  # return the move that was most visited
